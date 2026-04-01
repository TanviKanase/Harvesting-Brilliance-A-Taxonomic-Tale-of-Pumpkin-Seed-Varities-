from flask import Flask, jsonify, request, render_template
import pickle


app = Flask(__name__)

FIELD_SPECS = [
    {"name": "Area", "label": "Area"},
    {"name": "Perimeter", "label": "Perimeter"},
    {"name": "Major_Axis_Length", "label": "Major Axis Length"},
    {"name": "Minor_Axis_Length", "label": "Minor Axis Length"},
    {"name": "Eccentricity", "label": "Eccentricity"},
    {"name": "Convex_Area", "label": "Convex Area"},
    {"name": "Equiv_Diameter", "label": "Equivalent Diameter"},
    {"name": "Solidity", "label": "Solidity"},
    {"name": "Extent", "label": "Extent"},
    {"name": "Roundness", "label": "Roundness"},
    {"name": "Aspect_Ratio", "label": "Aspect Ratio"},
    {"name": "Compactness", "label": "Compactness"},
]


try:
    model, scaler, encoder = pickle.load(open("model.pkl", "rb"))
except Exception:
    model = pickle.load(open("model.pkl", "rb"))
    scaler = None
    encoder = None


def format_seed_label(result):
    text = str(result).strip()
    label_mapping = {
        "0": "Çerçevelik",
        "1": "Ürgüp Sivrisi",
        "Cercevelik": "Çerçevelik",
        "Çercevelik": "Çerçevelik",
        "Çerçevelik": "Çerçevelik",
        "Urgup Sivrisi": "Ürgüp Sivrisi",
        "Ürgüp Sivrisi": "Ürgüp Sivrisi",
        "ÃœrgÃ¼p Sivrisi": "Ürgüp Sivrisi",
    }
    return label_mapping.get(text, text)


def run_prediction(form_values):
    values = [float(form_values[field["name"]]) for field in FIELD_SPECS]

    try:
        values_scaled = scaler.transform([values]) if scaler is not None else [values]
    except Exception:
        values_scaled = [values]

    prediction = model.predict(values_scaled)[0]

    try:
        result = encoder.inverse_transform([prediction])[0] if encoder is not None else None
    except Exception:
        result = None

    if result is None:
        class_mapping = {
            0: "Çerçevelik",
            1: "Ürgüp Sivrisi",
        }
        result = class_mapping.get(prediction, str(prediction))

    result = format_seed_label(result)
    return f"Your seed belongs to {result} class"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST", "GET"])
def predict():
    prediction_text = None
    result_state = "idle"
    form_values = {field["name"]: "" for field in FIELD_SPECS}

    if request.method == "POST":
        form_values.update(
            {field["name"]: request.form.get(field["name"], "").strip() for field in FIELD_SPECS}
        )

        try:
            prediction_text = run_prediction(form_values)
            result_state = "success"
        except Exception:
            prediction_text = "Invalid input. Please check your values."
            result_state = "error"

    return render_template(
        "predict.html",
        prediction_text=prediction_text,
        result_state=result_state,
        form_values=form_values,
        field_specs=FIELD_SPECS,
    )


@app.route("/predict-preview", methods=["POST"])
def predict_preview():
    payload = request.get_json(silent=True) or {}
    form_values = {field["name"]: str(payload.get(field["name"], "")).strip() for field in FIELD_SPECS}

    if any(not value for value in form_values.values()):
        return jsonify(
            {
                "result_state": "idle",
                "prediction_text": "Enter all values to preview the result.",
            }
        )

    try:
        prediction_text = run_prediction(form_values)
        return jsonify(
            {
                "result_state": "success",
                "prediction_text": prediction_text,
            }
        )
    except Exception:
        return jsonify(
            {
                "result_state": "error",
                "prediction_text": "Invalid input. Please check your values.",
            }
        )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

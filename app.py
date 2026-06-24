import logging
import os
import traceback
import uuid

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from utils.sequence_analyzer import SequenceAnalyzer
from utils.neutralization_predictor import neutralization_predictor

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"fasta", "fa", "txt", "seq"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

_analyzer = None


def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = SequenceAnalyzer()
    return _analyzer


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def build_response(result, detected_mutations):
    raw_prediction = neutralization_predictor.predict_variant_neutralization(detected_mutations)
    details = result.get("details", {})

    return {
        "success": True,
        "similarity_score": float(result.get("similarity_score", 100)),
        "sequence_info": {
            "length": int(details.get("sequence_length", 0)),
            "gc_content": float(details.get("gc_content", 0)),
        },
        "mutations": {
            "list": detected_mutations,
            "has_d614g": bool(result.get("has_d614g", False)),
        },
        "variant": {
            "name": result.get("variant"),
            "confidence": result.get("variant_confidence"),
        },
        "neutralization_results": raw_prediction,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file selected"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Use .fasta, .fa, .txt, or .seq"}), 400

    safe_name = secure_filename(file.filename)
    filename = os.path.join(app.config["UPLOAD_FOLDER"], f"{uuid.uuid4().hex}_{safe_name}")

    try:
        file.save(filename)
        result = get_analyzer().analyze_sequence_file(filename)

        if not isinstance(result, dict):
            return jsonify({"error": "Analyzer returned invalid data"}), 500

        if not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", "Analysis failed"),
                "similarity_score": result.get("similarity_score", 0),
            }), 400

        detected = result.get("detected_mutations", {})
        if isinstance(detected, dict):
            detected_mutations = list(detected.keys())
        elif isinstance(detected, list):
            detected_mutations = detected
        else:
            detected_mutations = []

        logger.info("Detected mutations: %s", detected_mutations)
        return jsonify(build_response(result, detected_mutations))

    except Exception as exc:
        logger.exception("Upload analysis failed")
        return jsonify({"error": str(exc)}), 500

    finally:
        if os.path.exists(filename):
            os.remove(filename)


@app.route("/health")
def health():
    # Keep this endpoint lightweight so Render's 5s health check passes on cold start.
    return jsonify({"status": "ok"}), 200


@app.route("/ready")
def ready():
    analyzer = get_analyzer()
    return jsonify({
        "status": "ok",
        "predictor_ready": neutralization_predictor.ready,
        "references_loaded": len(analyzer.reference_genome or ""),
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

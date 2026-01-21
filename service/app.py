from flask import Flask, request, jsonify
import os
import logging
from datetime import datetime

UPLOAD_DIR = "./uploads"
LOG_DIR = "./logs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=f"{LOG_DIR}/document-service.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        logging.error("No file part in request")
        return jsonify({"error": "file is required"}), 400

    file = request.files["file"]
    if file.filename == "":
        logging.error("Empty filename received")
        return jsonify({"error": "filename missing"}), 400

    filepath = os.path.join(UPLOAD_DIR, file.filename)
    file.save(filepath)

    metadata = {
        "filename": file.filename,
        "size_bytes": os.path.getsize(filepath),
        "uploaded_at": datetime.utcnow().isoformat()
    }

    logging.info(f"Document uploaded: {metadata}")
    return jsonify(metadata), 201


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"service": "document-metadata", "status": "running"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

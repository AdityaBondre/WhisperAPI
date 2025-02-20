from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the Whisper model
model = whisper.load_model("base")

# Define upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Transcribe the audio
    result = model.transcribe(filepath)
    
    # Delete the file after processing
    os.remove(filepath)

    return jsonify({"transcription": result["text"]})

@app.route("/", methods=["GET"])
def home():
    return "Whisper API is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

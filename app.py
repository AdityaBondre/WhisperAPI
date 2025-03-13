from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import ollama
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load Whisper model
model = whisper.load_model("base")

# Define upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Function to summarize text using Ollama
def summarize_text(text):
    if not text or len(text.strip()) < 10:  # If transcription is null or too short, return as-is
        return text

    try:
        response = ollama.chat(
            model="mistral",  # Upgraded to a more powerful model
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes medical consultations. Focus only on the patient's symptoms and the doctor's diagnosis or treatment recommendations. Exclude all casual talk and unrelated details. Provide the summary in 3-5 concise bullet points."
                },
                {
                    "role": "user",
                    "content": f"Summarize the following doctor-patient conversation in 3-5 bullet points, focusing only on the patient's symptoms and the doctor's diagnosis or treatment recommendations:\n\n{text}"
                }
            ]
        )
        return response.get("message", {}).get("content", text)  # Return summary or original text
    except Exception as e:
        return text  # If summarization fails, return original text

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        # 🎧 Transcribe audio using Whisper
        result = model.transcribe(filepath)
        transcription = result.get("text", "").strip()
        print("🎧 Transcription:", transcription)

        # If transcription is empty, return it directly
        if not transcription:
            return jsonify({"summary": transcription})

        # 📝 Summarize using Ollama (mistral)
        summary = summarize_text(transcription)
        print("📝 Summary:", summary)

        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route("/", methods=["GET"])
def home():
    return "Whisper & Ollama API is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

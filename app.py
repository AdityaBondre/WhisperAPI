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
    try:
        response = ollama.chat(
            model="smollm2:360m",  # Use the smollm2:360m model
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes medical consultations. Focus only on the patient's problems and the doctor's observations or recommendations. Exclude casual talk, greetings, and unrelated details. Provide the summary in concise bullet points."
                },
                {
                    "role": "user",
                    "content": f"Summarize the following doctor-patient conversation in bullet points, focusing only on the patient's problems and the doctor's observations or recommendations:\n\n{text}"
                }
            ]
        )
        return response.get("message", {}).get("content", "No summary found")
    except Exception as e:
        return f"Summarization failed: {str(e)}"
    
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
        transcription = result.get("text", "No transcription found")
        print("🎧 Transcription:", transcription)

        # 📝 Summarize using Ollama with smollm2:360m
        summary = summarize_text(transcription)
        print("📝 Summary:", summary)

        # Fallback if summarization fails or quality is poor
        if "Summarization failed" in summary or len(summary.strip()) < 10:  # Adjust threshold as needed
            summary = "Summary unavailable. Here's the full transcription:\n\n" + transcription

        return jsonify({
            "summary": summary  # Return summary or fallback transcription
        })

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

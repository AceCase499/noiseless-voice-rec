# myapp.py
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import uuid
import os
import json
import logging
import re
import subprocess
from urllib.parse import urlparse

app = FastAPI()

# Allow React Native/Expo frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    # Save uploaded file
    input_filename = f"{uuid.uuid4()}_{file.filename}"
    input_path = os.path.join(UPLOAD_DIR, input_filename)

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Output path for processed audio
    output_filename = input_filename.replace(".wav", "_processed.wav")
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Run fast-music-remover
    try:
            logging.info(f"Processing media file with path: {media_path}")

            result = subprocess.run(
                ["./MediaProcessor/build/MediaProcessor", str(media_path)], capture_output=True, text=True
            )

            # Propagate MediaProcessor outputs
            logging.debug(f"MediaProcessor stdout: {result.stdout}")
            logging.error(f"MediaProcessor stderr: {result.stderr}")

            if result.returncode != 0:
                logging.error("MediaProcessor returned a non-zero exit code.")
                return None

            # Parse output
            for line in result.stdout.splitlines():
                if "Video processed successfully" in line or "Audio processed successfully" in line:
                    processed_media_path = line.split(": ", 1)[1].strip()

                    # Remove any surrounding quotes
                    if processed_media_path.startswith('"') and processed_media_path.endswith('"'):
                        processed_media_path = processed_media_path[1:-1]

                    processed_media_path = os.path.abspath(processed_media_path)
                    logging.info(f"Processed media path returned: {processed_media_path}")
                    return processed_media_path

            logging.error("No processed file path found in MediaProcessor output.")
            return None

    except Exception as e:
        logging.error(f"Error running MediaProcessor binary: {e}")
        return None

    return FileResponse(output_path, media_type="audio/wav", filename=output_filename)

app.run(port=8080, debug=True)
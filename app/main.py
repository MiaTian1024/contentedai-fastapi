from fastapi import FastAPI, Response, status, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment 
from audio.audio import Audio


app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to my api"}


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    input = file.filename
    audio_file = Audio(input)
    output = audio_file.convert_to_mp3()

    input_size = audio_file.get_size(input)
    output_size = audio_file.get_size(output)
    input_size_mb = round(input_size / (1024**2), 2)
    output_size_mb = round(output_size / (1024**2), 2)

    if output_size_mb > 25:
        audio_obj = AudioSegment.from_mp3(output)
        transcription = audio_file.get_chunks(audio_obj)
    else:
        transcription = audio_file.get_transcribe(output)
        transcription = str(transcription['text'])

    # Remove the temporary converted file
    audio_file.remove_temporary_files(output)
    audio_file.remove_temporary_files(input)
    
    return {"name":file.filename,
            "data": transcription,
            "input_size": "Size of " + file.filename + " is " + str(input_size_mb) +" MB",
            "output_size": "Size of " + output + " is " + str(output_size_mb) +" MB"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
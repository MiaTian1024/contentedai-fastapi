from fastapi import FastAPI, Response, status, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment 
import os
import openai
from pydub import AudioSegment 
from dotenv import dotenv_values
import shutil

openai_api_key = os.environ.get("OPENAI_API_KEY")

class Audio:
    def __init__(self, input):
        self.input = input

    def convert_to_mp3(self):
        # Convert other audio formats to MP3 
        name, ext = os.path.splitext(self.input)
        if ext != ".mp3":
            output = f"{name}.mp3"
            sound = AudioSegment.from_file(self.input)
            # Export the MP3 file
            sound.export(output, format="mp3")
        else:
            output = self.input
        return output
    
    def convert_to_wav(self):
        # Convert other audio formats to MP3 
        name, ext = os.path.splitext(self.input)
        if ext != ".wav":
            output = f"{name}.wav"
            sound = AudioSegment.from_file(self.input)
            # Export the wav file
            sound.export(output, format="wav")
        else:
            output = self.input
        return output
    
    def get_size(self, file):
        # Get the size of an audio file
        size = os.path.getsize(file)
        size_mb = round(size / (1024**2), 2)
        print(f"Size of {file} is {size_mb} MB")
        return size

    def get_transcribe(self, output):
        # Transcribe audio files
        openai.api_key = openai_api_key
        audio_file = open(output, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript

    def remove_directory(self, directory_path):
        try:
            # Use shutil.rmtree to remove the directory and its contents
            shutil.rmtree(directory_path)
            print(f"Successfully deleted directory: {directory_path}")
        except Exception as e:
            print(f"Error deleting directory: {e}")

    def remove_temporary_files(self, file_path):
        try:     
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Successfully removed file: {file_path}")
        except Exception as e:
            print(f"Error removing files: {e}")

    def get_chunks(self, audio):      

        one_minute = 60 * 1000
        chunk_unit = one_minute *20

        # Create a directory to store the chunks
        output_dir = "output_audio"
        os.makedirs(output_dir, exist_ok=True)

        # Initialize an empty list to store transcriptions
        transcriptions = []

        # Initialize the start time of the current chunk
        chunk_start = 0

        while chunk_start < len(audio):
            # Calculate the end time of the current chunk
            chunk_end = min(chunk_start + chunk_unit, len(audio))

            # Extract the current chunk
            chunk = audio[chunk_start:chunk_end]

            # Define the output file name for the current chunk
            chunk_name = f"chunk_{chunk_start / one_minute + 1}.mp3"
            chunk_path = os.path.join(output_dir, chunk_name)

            # Export the current chunk to a file
            chunk.export(chunk_path, format="mp3")

            # Transcribe the current chunk and append the result to transcriptions
            transcription = self.get_transcribe(chunk_path)["text"]
            transcriptions.append(transcription)

            # Update the start time for the next chunk
            chunk_start = chunk_end

        # Merge transcriptions into a single text
        merged_transcription = ' '.join(transcriptions)

        # Remove audio_chunks directory
        self.remove_directory(output_dir)

        return merged_transcription
    


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
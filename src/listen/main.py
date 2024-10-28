import os
import yaml
import pyaudio
import wave
import tempfile
from openai import OpenAI
import tkinter as tk
import threading

config_path = os.path.expanduser('~/.config/ai-utils.yaml')

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

client = OpenAI(api_key=config['keys']['openai'])

# PyAudio configuration
FORMAT = pyaudio.paInt16  # Audio format (16-bit int)
CHANNELS = 1              # Number of audio channels (mono)
RATE = 16000              # Sampling rate (16 kHz)
CHUNK = 1024              # Buffer size

def listen_and_transcribe():
    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open audio stream
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK)

    audio_data = []
    listening = True

    def stop_listening():
        nonlocal listening
        listening = False

    # Create GUI window
    root = tk.Tk()
    root.title("Recording")
    root.geometry("300x100")

    label = tk.Label(root, text="Press Enter to stop recording...")
    label.pack(pady=20)

    root.bind('<Return>', lambda event: stop_listening())

    def record_audio():
        nonlocal audio_data
        while listening:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data.append(data)

        # Close the recording window
        root.quit()

        # Stop the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            # Write audio data to a WAV file
            with wave.open(tmp_file.name, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(audio_data))

            # Transcribe the audio file
            transcribe(tmp_file)

    # Start recording in a separate thread
    threading.Thread(target=record_audio).start()

    root.mainloop()

def transcribe(file):
    try:
        with open(file.name, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            print(transcription.text)
    except Exception as e:
        print(f"Error during transcription: {e}")

# Call the new function to start recording and show GUI
def main():
    listen_and_transcribe()

if __name__ == "__main__":
    main()
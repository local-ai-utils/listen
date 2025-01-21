import tkinter as tk
import threading
import pyaudio
import wave
import tempfile

# PyAudio configuration
FORMAT = pyaudio.paInt16  # Audio format (16-bit int)
CHANNELS = 1              # Number of audio channels (mono)
RATE = 16000              # Sampling rate (16 kHz)
CHUNK = 1024              # Buffer size

def kickoff_gui(stop_event):
    root = tk.Tk()

    def stop_listening():
        stop_event.set()
        root.destroy()

    root.title("Recording")
    root.geometry("300x100")
    root.focus_force()
    root.lift()
    root.attributes("-topmost", True)
    root.bind('<Return>', lambda event: stop_listening())

    label = tk.Label(root, text="Enter to stop recording...")
    label.pack(pady=20)

    root.mainloop()

class RecordingThread(threading.Thread):
    def __init__(self, stop_event):
        super().__init__()
        self.stop_event = stop_event
        self.result = None

    def run(self):
        from local_ai_utils_core import LocalAIUtilsCore

        core = LocalAIUtilsCore()
        client = core.clients.open_ai()

        # Initialize PyAudio 
        audio = pyaudio.PyAudio()

        # Open audio stream
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                            input=True, frames_per_buffer=CHUNK)

        audio_data = []

        while not self.stop_event.is_set():
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data.append(data)

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
            self.result = transcribe(client, tmp_file)

def transcribe(client, file):
    try:
        with open(file.name, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            
            return transcription.text
    except Exception as e:
        print(f"Error during transcription: {e}")

# Call the new function to start recording and show GUI
def main():
    # Create an event to coordinate between threads
    stop_event = threading.Event()
    recording_thread = RecordingThread(stop_event)
    recording_thread.start()
    kickoff_gui(stop_event)

    recording_thread.join()
    print("thread result: ", recording_thread.result)
    

if __name__ == "__main__":
    main()
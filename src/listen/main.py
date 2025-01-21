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

def kickoff_gui(stop_event, recording_thread):
    root = tk.Tk()
    process_thread = None

    def stop_listening(event=None):
        nonlocal process_thread
        stop_event.set()

        process_thread = threading.Thread(target=process_audio, args=(recording_thread,))
        process_thread.start()

        root.quit()
        root.destroy()

        print('tell it to quit')
        root.after(0, process_thread.join)
        print('after tell it to quit')

    # Center the window on screen
    window_width = 500
    window_height = 80
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)

    root.focus_force()
    root.lift()
    root.attributes("-topmost", True)

    frame = tk.Frame(
        root,
    )
    frame.pack(fill='both', expand=True, padx=0, pady=0)

    label = tk.Label(
        root,
        text="⏺ Recording... Press Enter to stop",
        font=("Helvetica", 24)
    )

    label.place(relx=0.5, rely=0.5, anchor='center')

    root.bind('<Return>', stop_listening)

    # Remove decoration from the window, but do this last
    # to avoid UI bugs. tkinter will sometimes "lose" the window
    # after overriding redirects, and won't apply some settings
    root.title("")
    root.overrideredirect(True)

    # Only set the geometry after overrideredirect, because apparently that gets unset
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    root.mainloop()

class RecordingThread(threading.Thread):
    def __init__(self, stop_event):
        super().__init__()
        self.stop_event = stop_event
        self.result = None

    def run(self):
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

        self.result = {
            'audio': audio,
            'data': audio_data
        }

def save_audio(audio):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        # Write audio data to a WAV file
        with wave.open(tmp_file.name, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio['audio'].get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(audio['data']))

        return tmp_file

def transcribe(file):
    from local_ai_utils_core import LocalAIUtilsCore
    core = LocalAIUtilsCore()
    client = core.clients.open_ai()

    try:
        with open(file.name, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

            return transcription.text
    except Exception as e:
        print(f"Error during transcription: {e}")

def process_audio(recording_thread):
    print('start processing audio')
    recording_thread.join()
    audio = recording_thread.result
    tempfile = save_audio(audio)
    transcription = transcribe(tempfile)
    print(transcription)

# Call the new function to start recording and show GUI
def main():
    # Create an event to coordinate between threads
    stop_event = threading.Event()
    recording_thread = RecordingThread(stop_event)
    recording_thread.start()
    kickoff_gui(stop_event, recording_thread)
    

if __name__ == "__main__":
    main()
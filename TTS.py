import os
import tkinter as tk
from tkinter import Toplevel, ttk
from PIL import ImageGrab
import pytesseract
from google.cloud import texttospeech
import tempfile
import pygame
import atexit
import anthropic

path = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Set this to the path of your Google Cloud service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\jonat\source\\repos\\Python projects\\TextReader\\google_TTS\\text-to-speechifier-11df0c0c9fb0.json"
gtts_client = texttospeech.TextToSpeechClient()

anthropic_client = anthropic.Anthropic(
    api_key = os.getenv('ANTHROPIC_API_KEY'),
)

class ScreenSelect(Toplevel):
    def __init__(self, callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback
        self.begin_x = None
        self.begin_y = None
        self.end_x = None
        self.end_y = None
        self.rect = None  # Ensure rect is initialized here

        self.canvas = tk.Canvas(self, cursor="cross", bg='grey', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.attributes("-fullscreen", True, "-alpha", 0.3)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.begin_x = event.x
        self.begin_y = event.y

    def on_move_press(self, event):
        curX, curY = (event.x, event.y)
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.begin_x, self.begin_y, curX, curY, outline='red', width=2)
        else:
            self.canvas.coords(self.rect, self.begin_x, self.begin_y, curX, curY)

    def on_button_release(self, event):
        self.end_x, self.end_y = (event.x, event.y)
        self.destroy()
        self.callback(self.begin_x, self.begin_y, self.end_x, self.end_y)

class TextReaderApp:
    def __init__(self, master):
            self.master = master
            master.title("TextReader")
            pygame.mixer.init()
            self.setup_ui()
            self.temp_files = []
            atexit.register(self.cleanup_temp_files)

    def setup_ui(self):
        tk.Button(self.master, text="Select Region and Read Text", command=self.select_and_read).pack()
        tk.Button(self.master, text="Stop Playback", command=self.stop_playback).pack()

        # Anthropics System Response Instructions Input
        self.instructions_frame = tk.Frame(self.master)
        self.instructions_frame.pack(fill=tk.BOTH, expand=True)
        
        self.system_text_label = tk.Label(self.instructions_frame, text="System Instructions:")
        self.system_text_label.pack(side=tk.TOP, anchor="nw")
        
        # Create a scrollbar
        self.scrollbar = tk.Scrollbar(self.instructions_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create the Text widget with initial height, linking it to the scrollbar
        self.system_text_widget = tk.Text(self.instructions_frame, height=4, width=50, yscrollcommand=self.scrollbar.set)
        self.system_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.system_text_widget.yview)
        
        # Insert default value
        self.system_text_widget.insert(tk.END, "Translate the text into danish, making it as close as possible.")
        
        # Automatically adjust height up to a maximum
        self.system_text_widget.bind('<KeyRelease>', lambda e: self.adjust_text_widget_height())

        # Language Selection
        self.language_var = tk.StringVar(self.master)
        self.language_options = ["en-US", "en-GB", "fr-FR", "de-DE", "da-DK"]  # Example languages
        tk.Label(self.master, text="Language:").pack()
        tk.OptionMenu(self.master, self.language_var, *self.language_options).pack() 
        self.language_var.set(self.language_options[0])  # Default language

        # Gender Selection
        self.gender_var = tk.StringVar(self.master)
        self.gender_options = {"Neutral": texttospeech.SsmlVoiceGender.NEUTRAL,
                               "Male": texttospeech.SsmlVoiceGender.MALE,
                               "Female": texttospeech.SsmlVoiceGender.FEMALE}
        tk.Label(self.master, text="Voice Gender:").pack()
        tk.OptionMenu(self.master, self.gender_var, *self.gender_options.keys()).pack()
        self.gender_var.set("Neutral")  # Default gender

        # Speaking Rate
        self.speaking_rate_var = tk.DoubleVar(self.master, value=1.0)  # Default rate
        tk.Scale(self.master, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                 label="Speaking Rate", variable=self.speaking_rate_var).pack()

    def adjust_text_widget_height(self):
        # Adjust the height of the text widget according to its content, up to a max height
        max_height = 12
        current_lines = int(self.system_text_widget.index('end-1c').split('.')[0])
        new_height = min(current_lines + 1, max_height)  # Add 1 to consider the current line being edited
        self.system_text_widget.config(height=new_height)

    def get_screen_text(self, x1, y1, x2, y2):
        screen_capture = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        text = pytesseract.image_to_string(screen_capture)
        return text

    def text_to_speech(self, text):
        if text.strip():
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice_params = texttospeech.VoiceSelectionParams(
                language_code=self.language_var.get(),
                ssml_gender=self.gender_options[self.gender_var.get()])
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=self.speaking_rate_var.get())
            
            response = gtts_client.synthesize_speech(input=synthesis_input, voice=voice_params, audio_config=audio_config)
            temp_mp3 = tempfile.mktemp(suffix='.mp3')
            with open(temp_mp3, "wb") as out:
                out.write(response.audio_content)
                self.temp_files.append(temp_mp3)
            pygame.mixer.music.load(temp_mp3)
            pygame.mixer.music.play()

    def stop_playback(self):
        pygame.mixer.music.stop()

    def cleanup_temp_files(self):
        for file_path in self.temp_files:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Could not delete temporary file {file_path}: {e}")


    def select_and_read(self):
        self.master.withdraw()
        selector = ScreenSelect(self.process_selection, master=self.master)
        self.master.wait_window(selector)

    def get_anthropic_response(self, message):
        system_instruction = self.system_text_widget.get("1.0", "end-1c")  # Get text from the entry widget

        try:
            message = anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=100,
                temperature=0.0,
                system= "keep it short and mimic the original" + system_instruction,
                messages=[
                        {"role": "user", "content": message }
                ]
            )

            print(message.content[0].text)

            return message.content[0].text
        except Exception as err:
            print(f"An error occurred: {err}")
        return "I'm sorry, I couldn't process your request."

    def process_selection(self, x1, y1, x2, y2):
        text = self.get_screen_text(x1, y1, x2, y2)
        reply = self.get_anthropic_response(text)
        self.text_to_speech(reply)
        self.master.deiconify()

if __name__ == "__main__":
    pytesseract.pytesseract.tesseract_cmd = path
    root = tk.Tk()
    app = TextReaderApp(root)
    root.mainloop()

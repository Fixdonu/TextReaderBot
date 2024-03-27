# text_reader_app.py
import tkinter as tk
from screen_select import ScreenSelect
import pygame
import tempfile
from google.cloud import texttospeech
import os
import atexit
import anthropic
import os
from PIL import ImageGrab
import pytesseract
from google.cloud import texttospeech
from config import TESSERACT_PATH, GOOGLE_CREDENTIALS_PATH

anthropic_client = anthropic.Anthropic(
    api_key = os.getenv('ANTHROPIC_API_KEY'),
)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDENTIALS_PATH
gtts_client = texttospeech.TextToSpeechClient()

class TextReaderApp:
    def __init__(self):
            self.master = tk.Tk()
            self.master.title("TextReader")
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

    def get_screen_text(self, x1, y1, x2, y2):
        screen_capture = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        return pytesseract.image_to_string(screen_capture)

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
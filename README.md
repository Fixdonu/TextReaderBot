# Text Reader Application

This Text Reader application is a Python-based tool that allows users to select a screen region and reads out the text found within that area. It utilizes OCR (Optical Character Recognition) via Tesseract, Google Cloud's Text-to-Speech API, and Anthropics for text processing to convert the recognized text into speech, with customization options for language, voice gender, and speaking rate.

## Features

- Screen region selection for text capture.
- Text-to-Speech conversion with customizable language, voice gender, and speaking rate.
- Uses Tesseract for OCR, Google Cloud's Text-to-Speech API, and Anthropics for advanced text processing.

## Prerequisites

- Python 3.6 or later.
- Pytesseract.
- Google Cloud account with Text-to-Speech API enabled.
- Pygame for audio playback.
- An Anthropics account and API key.

## Setup

### 1. Clone the repository:
```bash
git clone [your-repository-url]
cd [your-repository-directory]
```

### 2. Install dependencies:
Make sure you have Python installed on your system. Then, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Tesseract-OCR Setup:

- Download and install Tesseract from [Tesseract's GitHub page](https://github.com/tesseract-ocr/tesseract).
- Update the '**TESSERACT_PATH**' in '**config.py**' to the path where Tesseract is installed on your machine.

### 4. Google Cloud Text-to-Speech Setup:

- Follow the instructions on Google Cloud's documentation to create a service account and download its credentials JSON file.
- Update the '**GOOGLE_CREDENTIALS_PATH**' in '**config.py**' with the path to your downloaded credentials JSON file.
Environment Variables:

### 5. Environment Variables:
Optionally, set the '**GOOGLE_APPLICATION_CREDENTIALS**' environment variable to the path of your Google Cloud credentials JSON file. This step might be platform-specific.

### 6. Anthropics Setup:
Create an account, get 5 dollars worth of api access, and [create a key to use](https://docs.anthropic.com/claude/docs/quickstart-guide#step-3-optional-set-up-your-api-key).

### Running the Application
To run the application, execute:

```bash
python main.py
```

Follow the GUI prompts to select a screen region and hear the captured text read aloud.

### Customizing Text-to-Speech
The application allows you to customize the language, voice gender, and speaking rate of the text-to-speech output through its GUI.

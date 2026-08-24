Maya English Voice Tutor

यह Python 3.12 और Streamlit में बना turn-by-turn English speaking practice
software है। आप microphone से English बोलते हैं, speech text में बदलती है,
Gemini जवाब तैयार करता है और Maya उस जवाब को Indian female English voice में
बोलती है।

मुख्य सुविधाएँ

Microphone से English voice input

Gemini 2.5 Flash-Lite से conversation

en-IN-NeerjaNeural Indian female voice

Beginner, Intermediate और Advanced levels

अलग-अलग practice topics

Gentle, conversation-only और detailed correction modes

पूरी chat history और end-of-session feedback

Text input fallback

UI के दाईं तरफ Designed by ER Pradeep Mavai

Project structure

maya_english_voice_tutor/
├── .streamlit/
│   └── config.toml
├── .env.example
├── .gitignore
├── app.py
├── config.py
├── gemini_agent.py
├── prompts.py
├── speech_utils.py
├── requirements.txt
└── README.md

VS Code में folder और files बनाना

Desktop पर maya_english_voice_tutor नाम का नया folder बनाएँ।

VS Code खोलें और File > Open Folder से वही folder खोलें।

Explorer में New File दबाकर ये files बनाएँ: app.py, config.py,
gemini_agent.py, prompts.py, speech_utils.py, requirements.txt,
.env.example, .gitignore और README.md।

New Folder दबाकर .streamlit बनाएँ। उसके अंदर config.toml बनाएँ।

इस project की हर supplied file का code उसी नाम वाली VS Code file में paste
करके Ctrl+S से save करें।

Python 3.12 check और virtual environment

VS Code में Terminal > New Terminal खोलें और PowerShell में चलाएँ:

py -3.12 --version
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

अगर py -3.12 --version काम नहीं करता, Python 3.12 install करते समय Add
Python to PATH चुनें। VS Code में Ctrl+Shift+P दबाएँ, Python: Select
Interpreter खोलें और .venv वाला Python चुनें।

Gemini की free API key लगाना

Browser में https://aistudio.google.com/apikey खोलें।

अपने Google account से sign in करें।

Create API key दबाएँ और key copy करें।

VS Code terminal में यह command चलाएँ:

Copy-Item .env.example .env

.env खोलें और value बदलें:

GEMINI_API_KEY=यहाँ_अपनी_वास्तविक_key_paste_करें

API key को quotation marks में रखने की जरूरत नहीं है। .env GitHub पर upload
नहीं होगी क्योंकि वह .gitignore में है।

App चलाना

Activated terminal में चलाएँ:

python -m streamlit run app.py

Browser में http://localhost:8501 खुलेगा। Chrome microphone permission पूछे
तो Allow करें। Settings चुनकर Start / Restart session दबाएँ, Maya का
welcome सुनें, फिर Record your English message से बोलें।

App को python app.py से न चलाएँ। ऐसा करने पर missing ScriptRunContext warning
आ सकती है। हमेशा python -m streamlit run app.py चलाएँ।

यह अंदर से कैसे काम करता है

Microphone recording
        ↓
SpeechRecognition (English - India)
        ↓
Gemini 2.5 Flash-Lite + recent conversation
        ↓
Maya का छोटा English reply और correction
        ↓
Neerja Indian female voice + Streamlit audio player

सामान्य errors और समाधान

ModuleNotFoundError

Virtual environment activate करके दोबारा चलाएँ:

.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

GEMINI_API_KEY नहीं मिली

जाँचें कि file का नाम ठीक .env है, .env.txt नहीं। Key paste करने के बाद app
बंद करके फिर चलाएँ।

Microphone नहीं दिख रहा

Chrome में address bar के lock/site-settings icon से microphone को Allow करें।
Windows में Settings > Privacy & security > Microphone के अंदर desktop apps
को permission दें।

Voice समझ नहीं आ रही

शांत कमरे में microphone के पास 5-15 seconds की साफ English बोलें। बहुत लंबी
recording न करें। जरूरत होने पर Type instead tab इस्तेमाल करें।

Gemini 429 error

Free-tier request limit पूरी हुई है। कुछ समय बाद दोबारा प्रयास करें। Free tier
की limits Google account, project, model और region के अनुसार बदल सकती हैं।

Maya का text दिख रहा है लेकिन आवाज़ नहीं

Internet connection जाँचें। Browser autoplay रोक सकता है; message के नीचे audio
player का Play button दबाएँ।

जरूरी अंतर

Ravan.ai का Agni enterprise phone-agent platform real-time, full-duplex calling,
telephony, analytics और sub-second infrastructure देता है। यह project personal
English practice के लिए free/low-cost learning prototype है: user recording
रोकता है, फिर Maya का जवाब आता है। यह phone calling software नहीं है।

Privacy note

इस version में recorded speech online speech-recognition service को और
conversation text Gemini API को भेजा जाता है। Password, bank details या दूसरी
sensitive information न बोलें।
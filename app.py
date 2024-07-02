import streamlit as st
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig, ResultReason
from openai import AzureOpenAI
import requests

# Azure Cognitive Services credentials
TTS_AZURE_API_KEY = st.secrets.TTS_AZURE_API_KEY
TTS_AZURE_REGION = st.secrets.TTS_AZURE_REGION

AZURE_OPENAI_ENDPOINT = st.secrets.AZURE_OPENAI_ENDPOINT
OPENAI_API_VERSION = st.secrets.OPENAI_API_VERSION
OPENAI_MODEL_DEPLOYMENT = st.secrets.OPENAI_MODEL_DEPLOYMENT
OPENAI_API_KEY = st.secrets.OPENAI_API_KEY

CHAT_API_ENDPOINT =  st.secrets.CHAT_API_ENDPOINT
AUTH_TOKEN =  st.secrets.AUTH_TOKEN


client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=OPENAI_API_KEY,
    api_version=OPENAI_API_VERSION
)


def get_chat_response(question:str):
    """Use Ejento to generate script of video based on topic"""
    overrides = {
            "semantic_ranker": True,
            "semantic_captions": False,
            "top": 3,
            "suggest_followup_questions": False,
            "sources": True,
            "cache_skip": True
        }
    req = {
        "auth-token":AUTH_TOKEN,
        "history": [
            {
            "user": question
            }
        ],
        "category": 871,
        "created_by": "faizan@datasciencedojo.com",
        "model_deployment": "gpt4-o",
        "approach": "rrr",
        "overrides": overrides,
        "query_source": "streamlit_demo",
        "user_id": 102,
        "email": "faizan@datasciencedojo.com"
        }
    # Make a JSON POST request to the API endpoint
    response = requests.post(CHAT_API_ENDPOINT, json=req)
    # print('status code',response.status_code)
    answer = response.json()
    final_answer = answer['answer']
    # print(final_answer)
    return final_answer


languages_and_voices = {
    "Arabic (Egypt)": ["ar-EG-SalmaNeural", "ar-EG-ShakirNeural"],
    "Arabic (Saudi Arabia)": ["ar-SA-HamedNeural", "ar-SA-ZariyahNeural"],
    "Chinese (Mandarin, Simplified)": ["zh-CN-XiaochenNeural", "zh-CN-XiaohanNeural"],
    "Chinese (Cantonese, Traditional)": ["zh-HK-HiuGaaiNeural", "zh-HK-HiuMaanNeural"],
    "Chinese (Taiwan, Traditional)": ["zh-TW-HsiaoChenNeural", "zh-TW-HsiaoYuNeural"],
    "Danish": ["da-DK-ChristelNeural", "da-DK-JeppeNeural"],
    "Dutch": ["nl-NL-ColetteNeural", "nl-NL-MaartenNeural"],
    "English (Australian)": ["en-AU-NatashaNeural", "en-AU-WilliamNeural"],
    "English (Canadian)": ["en-CA-ClaraNeural", "en-CA-LiamNeural"],
    "English (Indian)": ["en-IN-NeerjaNeural", "en-IN-PrabhatNeural"],
    "English (New Zealand)": ["en-NZ-MitchellNeural", "en-NZ-MollyNeural"],
    "English (South African)": ["en-ZA-LeahNeural", "en-ZA-LukeNeural"],
    "English (UK)": ["en-GB-RyanNeural", "en-GB-SoniaNeural"],
    "English (US)": ["en-US-JennyNeural", "en-US-GuyNeural"],
    "Finnish": ["fi-FI-NooraNeural", "fi-FI-SelmaNeural"],
    "French": ["fr-FR-DeniseNeural", "fr-FR-HenriNeural"],
    "German": ["de-DE-KatjaNeural", "de-DE-ConradNeural"],
    "Greek": ["el-GR-AthinaNeural", "el-GR-NestorasNeural"],
    "Hebrew": ["he-IL-AvriNeural", "he-IL-HilaNeural"],
    "Hindi": ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"],
    "Hungarian": ["hu-HU-NoemiNeural", "hu-HU-TamasNeural"],
    "Italian": ["it-IT-ElsaNeural", "it-IT-FabiolaNeural"],
    "Japanese": ["ja-JP-KeitaNeural", "ja-JP-NanamiNeural"],
    "Korean": ["ko-KR-InJoonNeural", "ko-KR-SunHiNeural"],
    "Norwegian": ["nb-NO-FinnNeural", "nb-NO-IselinNeural"],
    "Polish": ["pl-PL-MarekNeural", "pl-PL-ZofiaNeural"],
    "Portuguese (Brazilian)": ["pt-BR-AntonioNeural", "pt-BR-FranciscaNeural"],
    "Portuguese (Portugal)": ["pt-PT-DuarteNeural", "pt-PT-RaquelNeural"],
    "Russian": ["ru-RU-DariyaNeural", "ru-RU-NikolaiNeural"],
    "Spanish (Mexican)": ["es-MX-DaliaNeural", "es-MX-JorgeNeural"],
    "Spanish (Spain)": ["es-ES-ElviraNeural", "es-ES-AlvaroNeural"],
    "Swedish": ["sv-SE-MattiasNeural", "sv-SE-SofieNeural"],
    "Turkish": ["tr-TR-AhmetNeural", "tr-TR-EmelNeural"]
}

# Function to convert text to speech using Azure
def text_to_speech(text, tts_api_key, tts_region, voice):
    speech_config = SpeechConfig(subscription=tts_api_key, region=tts_region)
    speech_config.speech_synthesis_voice_name = voice
    audio_config = AudioConfig(filename="output.wav")
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    
    result = synthesizer.speak_text_async(text).get()
    if result.reason == ResultReason.SynthesizingAudioCompleted:
        return "output.wav"
    else:
        return None

# Function to convert text to speech using Azure
def translate_text(text, target_language, model_deployemnt):
    system_prompt = "You are an expert translater, which translated English text to any language user ask for. You must only return the translated text and nothing else."
    user_prompt = f"Translate the following text to {target_language}: {text}"
    messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    completion = client.chat.completions.create(
        model = model_deployemnt,  # Specify the engine
        messages = messages
    )
    return completion.choices[0].message.content

# Streamlit app

# Initialize session state variables
if 'text_input' not in st.session_state:
    st.session_state.text_input = ""
if 'generated_script' not in st.session_state:
    st.session_state.generated_script = ""

st.title("Text to Speech Converter")

st.write("Enter topic for video script generation")
video_topic = st.text_input("Enter your video topic here:")

if st.button('Generate script'):
    response = get_chat_response(video_topic)
    st.session_state.generated_script = response
    st.session_state.text_input = response  # Initialize text input with the generated script

# Persist the text input field
st.session_state.text_input = st.text_area(label="Enter your text here:", value=st.session_state.text_input)

selected_language = st.selectbox("Select Language", list(languages_and_voices.keys()))
selected_voice = st.selectbox("Select Voice", languages_and_voices[selected_language])

if st.button("Convert to Speech"):
    if st.session_state.text_input:
        translated_text = translate_text(st.session_state.text_input, selected_language, OPENAI_MODEL_DEPLOYMENT)
        st.write(f"Translated english text to {selected_language}")
        st.write(translated_text)
        output_file = text_to_speech(translated_text, TTS_AZURE_API_KEY, TTS_AZURE_REGION, selected_voice)
        st.write('Generated Audio ...')
        if output_file:
            audio_file = open(output_file, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/wav')
        else:
            st.error("An error occurred while converting the text to speech.")
    else:
        st.error("Please enter some text to convert.")


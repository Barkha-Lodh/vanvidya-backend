import requests
import json
import google.generativeai as genai
from groq import Groq
from deep_translator import GoogleTranslator
from decouple import config
from PIL import Image
import io
import os


# ─── WIKIPEDIA API ────────────────────────────────────────────────────
class WikipediaAPI:
    BASE_URL = 'https://en.wikipedia.org/api/rest_v1/page/summary/'
    
    PLANT_NAME_MAP = {
        'genda': 'Marigold', 'gulab': 'Rose', 'tulsi': 'Tulsi',
        'neem': 'Neem', 'champa': 'Champa', 'mogra': 'Jasmine',
    }
    
    @staticmethod
    def get_plant_info(plant_name):
        try:
            english_name = WikipediaAPI.PLANT_NAME_MAP.get(
                plant_name.lower(), plant_name)
            formatted = english_name.replace(' ', '_')
            url = f'{WikipediaAPI.BASE_URL}{formatted}'
            headers = {'User-Agent': 'VanVidya/1.0'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                description = data.get('extract', '')
                
                if 'may refer to' in description or 'can refer to' in description:
                    url2 = f'{WikipediaAPI.BASE_URL}{formatted}_plant'
                    response = requests.get(url2, headers=headers, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        description = data.get('extract', '')
                
                image_url = data.get('thumbnail', {}).get('source')
                wiki_url = data.get('content_urls', {}).get('desktop', {}).get('page')
                return description, image_url, wiki_url
        except Exception as e:
            print(f'Wikipedia error: {e}')
        return None, None, None


# ─── GROQ API ─────────────────────────────────────────────────────────
class GroqPlantAPI:
    @staticmethod
    def get_plant_data(plant_name):
        try:
            client = Groq(api_key=config('GROQ_API_KEY'))
            
            prompt = f'''Give plant details for "{plant_name}".
Return ONLY JSON with these fields:
scientific_name, family, hindi_name, watering, sunlight, soil_type, 
indoor_outdoor, edible, toxic, warning, origin, growth_rate, fun_facts, 
diseases (array with name, symptom, treatment).
Only JSON no markdown.'''
            
            response = client.chat.completions.create(
                messages=[{'role': 'user', 'content': prompt}],
                model='llama-3.3-70b-versatile',
                temperature=0.2
            )
            
            text = response.choices[0].message.content.strip()
            
            # Clean markdown
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            return json.loads(text)
            
        except Exception as e:
            print(f'Groq error: {e}')
            return None


# ─── GEMINI API (OLD PACKAGE) ─────────────────────────────────────────
class GeminiPlantAPI:
    @staticmethod
    def get_plant_data(plant_name):
        try:
            genai.configure(api_key=config('GEMINI_API_KEY'))
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            prompt = f'''Give detailed information about "{plant_name}".
Return ONLY JSON:
{{
    "scientific_name": "",
    "family": "",
    "hindi_name": "real Hindi word not transliteration",
    "watering": "",
    "sunlight": "",
    "soil_type": "",
    "indoor_outdoor": "",
    "edible": "",
    "toxic": "",
    "warning": "",
    "origin": "",
    "growth_rate": "",
    "fun_facts": "",
    "diseases": [{{"name":"","symptom":"","treatment":""}}]
}}
Only JSON no markdown.'''
            
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            return json.loads(text)
            
        except Exception as e:
            print(f'Gemini error: {e}')
            return None
    
    @staticmethod
    def identify_from_image(image_file):
        try:
            genai.configure(api_key=config('GEMINI_API_KEY'))
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            pil_image = Image.open(io.BytesIO(image_file.read()))
            
            prompt = '''Analyze this leaf image.
Return ONLY JSON:
{
    "plant_name": "common name",
    "confidence": 85,
    "scientific_name": "",
    "is_healthy": true or false,
    "disease": {
        "name": "disease or null",
        "severity": "low/medium/high or null",
        "symptoms": "",
        "treatment": ""
    }
}
If unknown set plant_name to 'Unknown'. If healthy set disease to null.'''
            
            response = model.generate_content([prompt, pil_image])
            text = response.text.strip()
            
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            return json.loads(text)
            
        except Exception as e:
            print(f'Gemini Vision error: {e}')
            return None


# ─── GOOGLE TRANSLATE ─────────────────────────────────────────────────
class GoogleTranslateAPI:
    @staticmethod
    def translate_to_hindi(text):
        try:
            translated = GoogleTranslator(
                source='en', target='hi').translate(text)
            return translated
        except:
            return text
        
# Railway deployment


if os.environ.get('RAILWAY_ENVIRONMENT'):
    # Production mode on Railway
    DEBUG = False
    ALLOWED_HOSTS = ['.railway.app', '.up.railway.app']
else:
    # Development mode on laptop
    DEBUG = True
    ALLOWED_HOSTS = ['*']
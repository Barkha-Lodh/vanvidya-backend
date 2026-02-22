import requests
import json
import google.generativeai as genai
from groq import Groq
from deep_translator import GoogleTranslator
from decouple import config
from PIL import Image
import io


# ═══════════════════════════════════════════════════════════════════════
# HELPER FUNCTION
# ═══════════════════════════════════════════════════════════════════════
def format_plant_data(data):
    """Format boolean or short values into descriptive text"""
    if not data:
        return data
    
    # Format edible field
    edible = data.get('edible', '')
    if isinstance(edible, str):
        edible_lower = edible.lower()
        if edible_lower in ['true', 'yes', 'edible']:
            data['edible'] = "Yes, safe to consume (verify parts and preparation)"
        elif edible_lower in ['false', 'no', 'not edible', 'inedible']:
            data['edible'] = "Not edible, not safe for consumption"
        elif len(edible) < 10:
            data['edible'] = "Edibility information not available"
    elif edible is True:
        data['edible'] = "Yes, safe to consume (verify parts and preparation)"
    elif edible is False:
        data['edible'] = "Not edible, not safe for consumption"
    
    # Format toxic field
    toxic = data.get('toxic', '')
    if isinstance(toxic, str):
        toxic_lower = toxic.lower()
        if toxic_lower in ['false', 'no', 'non-toxic', 'safe']:
            data['toxic'] = "Non-toxic and safe for humans and pets"
        elif toxic_lower in ['true', 'yes', 'toxic', 'poisonous']:
            data['toxic'] = "Contains toxic compounds, avoid ingestion"
        elif len(toxic) < 10:
            data['toxic'] = "Toxicity information not available"
    elif toxic is True:
        data['toxic'] = "Contains toxic compounds, avoid ingestion"
    elif toxic is False:
        data['toxic'] = "Non-toxic and safe for humans and pets"
    
    return data


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
            
            # UPDATED PROMPT - More descriptive
            prompt = f'''Give plant details for "{plant_name}".
Return ONLY JSON with:
- scientific_name, family, hindi_name
- watering (describe frequency), sunlight (describe needs)
- soil_type, indoor_outdoor
- edible (describe which parts or say "Not edible")
- toxic (describe toxicity or say "Non-toxic")
- warning, origin, growth_rate, fun_facts
- diseases array with name, symptom, treatment
Be descriptive for edible and toxic fields. Only JSON no markdown.'''
            
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
            
            # Parse JSON and format
            result = json.loads(text)
            result = format_plant_data(result)  # ← FORMAT DATA!
            
            return result
            
        except Exception as e:
            print(f'Groq error: {e}')
            return None


# ─── GEMINI API ───────────────────────────────────────────────────────
class GeminiPlantAPI:
    @staticmethod
    def get_plant_data(plant_name):
        try:
            genai.configure(api_key=config('GEMINI_API_KEY'))
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # UPDATED PROMPT - Better instructions
            prompt = f'''Give detailed information about the plant "{plant_name}".
Return ONLY JSON in this exact format:
{{
    "scientific_name": "scientific name here",
    "family": "plant family",
    "hindi_name": "actual Hindi word not transliteration",
    "watering": "watering frequency and amount",
    "sunlight": "sunlight requirements",
    "soil_type": "soil type needed",
    "indoor_outdoor": "Indoor or Outdoor or Both",
    "edible": "Describe if edible and which parts, or 'Not edible for consumption'",
    "toxic": "Describe toxicity level and effects, or 'Non-toxic and safe'",
    "warning": "Any warnings or precautions, or null if none",
    "diseases": [
        {{
            "name": "disease name",
            "symptom": "symptoms",
            "treatment": "treatment method",
        }}
    "origin": "native region",
    "growth_rate": "growth rate",
    "fun_facts": "interesting facts"
    ]
}}

IMPORTANT:
- For "edible": Write full sentence describing which parts are edible
- For "toxic": Write full sentence describing toxicity
- For mushrooms: Specify if poisonous and severity
- Be detailed and specific

Return ONLY the JSON, no markdown.'''
            
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean markdown
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            # Parse JSON and format
            result = json.loads(text)
            result = format_plant_data(result)  # ← FORMAT DATA!
            
            return result
            
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
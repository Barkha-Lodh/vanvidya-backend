import sqlite3, requests, json, time
import google.generativeai as genai
from decouple import Config

config = Config('.env')
genai.configure(api_key=config('GEMINI_API_KEY'))
OUTPUT_DB = 'plants_offline.db'

PLANTS_LIST = [
    'Rose','Tulsi','Neem','Marigold','Sunflower','Lotus',
    'Hibiscus','Jasmine','Aloe Vera','Money Plant','Snake Plant',
    'Bamboo','Mango','Banana','Orchid','Lily','Basil',
    'Mint','Coriander','Lavender','Cactus','Button Mushroom'
]

def get_wikipedia(name):
    try:
        url = f'https://en.wikipedia.org/api/rest_v1/page/summary/{name.replace(chr(32),chr(95))}'
        r = requests.get(url, headers={'User-Agent':'VanVidya/1.0'}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            desc = data.get('extract','')
            if 'may refer to' not in desc:
                return desc[:600], data.get('thumbnail',{}).get('source')
    except: pass
    return None, None

def get_gemini(name):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        prompt = f'''Plant "{name}" JSON: scientific_name, family, hindi_name,
watering, sunlight, soil_type, indoor_outdoor, edible, toxic, warning,
origin, growth_rate, fun_facts, diseases. Only JSON.'''
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        if '```json' in text: text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text: text = text.split('```')[1].split('```')[0].strip()
        return json.loads(text)
    except: return None

conn = sqlite3.connect(OUTPUT_DB)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS plants (
    id INTEGER PRIMARY KEY, common_name TEXT, hindi_name TEXT,
    scientific_name TEXT, family TEXT, description TEXT, image_url TEXT,
    watering TEXT, sunlight TEXT, soil_type TEXT, indoor_outdoor TEXT,
    edible TEXT, toxic TEXT, warning TEXT, origin TEXT, growth_rate TEXT,
    fun_facts TEXT, diseases TEXT, category TEXT)''')
conn.commit()

for i, name in enumerate(PLANTS_LIST):
    print(f'[{i+1}/{len(PLANTS_LIST)}] {name}...')
    c.execute('SELECT id FROM plants WHERE common_name=?', (name,))
    if c.fetchone(): continue
    desc, img = get_wikipedia(name)
    data = get_gemini(name)
    if data:
        c.execute('''INSERT INTO plants (common_name,hindi_name,scientific_name,
            family,description,image_url,watering,sunlight,soil_type,indoor_outdoor,
            edible,toxic,warning,origin,growth_rate,fun_facts,diseases,category)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (name, data.get('hindi_name',''), data.get('scientific_name',''),
             data.get('family',''), desc or 'Not available', img,
             data.get('watering',''), data.get('sunlight',''),
             data.get('soil_type',''), data.get('indoor_outdoor',''),
             data.get('edible',''), data.get('toxic',''), data.get('warning'),
             data.get('origin',''), data.get('growth_rate',''),
             data.get('fun_facts',''), json.dumps(data.get('diseases',[])),
             'Plant'))
        conn.commit()
        time.sleep(2)
conn.close()
print(f'Done! Copy {OUTPUT_DB} to Android assets/')

import os
import requests
import pandas as pd
from flask import Flask, render_template, request, jsonify
from PIL import ImageFont
import html
import re
from markupsafe import Markup

app = Flask(__name__)
hadith_data = pd.read_excel("hadith.xlsx")

# Load Quran font
FONT_PATH = "quran.ttf"
try:
    font = ImageFont.truetype(FONT_PATH, 24)
except IOError:
    font = ImageFont.load_default()

def escape_html(text):
    return html.escape(str(text))

def get_surahs():
    url = "https://api.alquran.cloud/v1/surah"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']
    return []

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/quran')
def quran():
    surahs = get_surahs()
    return render_template("quran.html", surahs=surahs)

@app.route('/ayah', methods=['POST'])
def ayah():
    surah = request.json.get('surah')
    ayah = request.json.get('ayah')

    try:
        arabic_url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/ar"
        arabic_text = requests.get(arabic_url).json()['data']['text']

        kurdish_url = f"https://quranenc.com/api/v1/translation/aya/kurdish_salahuddin/{surah}/{ayah}"
        kurdish_text = requests.get(kurdish_url).json()['result']['translation']

        audio_url = f"https://everyayah.com/data/Alafasy_64kbps/{str(surah).zfill(3)}{str(ayah).zfill(3)}.mp3"

        return jsonify({
            "arabic": escape_html(arabic_text),
            "kurdish": escape_html(kurdish_text),
            "audio": audio_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/hadith')
def hadith():
    query = request.args.get('query', '').strip()
    if query:
        def highlight(text):
            pattern = re.compile(re.escape(query), re.IGNORECASE)
            return Markup(pattern.sub(
                lambda m: f"<span style='color:red; font-weight:bold;'>{m.group(0)}</span>",
                str(text)
            ))

        filtered = hadith_data[
            hadith_data['hadith_ar'].astype(str).str.contains(query, case=False, na=False) |
            hadith_data['hadith_ku'].astype(str).str.contains(query, case=False, na=False) |
            hadith_data['hadith_geranawa'].astype(str).str.contains(query, case=False, na=False) |
            hadith_data['hadith_id'].astype(str).str.contains(query, case=False, na=False)
        ].copy()

        filtered['hadith_ar'] = filtered['hadith_ar'].apply(highlight)
        filtered['hadith_ku'] = filtered['hadith_ku'].apply(highlight)
        filtered['hadith_geranawa'] = filtered['hadith_geranawa'].apply(highlight)
        filtered['hadith_id'] = filtered['hadith_id'].apply(highlight)
    else:
        filtered = hadith_data.copy()

    return render_template("hadith.html", hadiths=filtered.to_dict(orient="records"), query=query)


if __name__ == '__main__':
    app.run(debug=True)

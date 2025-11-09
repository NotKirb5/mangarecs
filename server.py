from flask import Flask, render_template, request, jsonify
import requests
import base64
import time
import main
import json

app = Flask(__name__)

@app.route("/")

def index():
    return render_template('index.html')


@app.route('/api/singlemanga')
def singlemanga():
    title = request.args.get('title','')
    return jsonify({'data':main.getmangabyname(title)})
    
@app.route('/api/mangarecs')
def mangarecs():
    userdata = request.args.get('manga','')
    recdata = main.getRecs(userdata)
    return jsonify(recdata)

@app.route('/api/fetchmanga')
def fetchmanga():
    id = request.args.get('id','')
    resp = requests.get(f'https://api.mangadex.org/manga/{id}?includes[]=cover_art')
    if resp.status_code == 200:
        return jsonify(json.loads(resp.text))
    else:
        return jsonify({'error',resp.status_code})

@app.route('/api/mangasearch')
def mangasearch():
    title = request.args.get('title','')
    url = f'https://api.mangadex.org/manga?title={title}&limit=5'
    response = requests.get(url)
    return jsonify(response.json())

cache = {}  # { key: { 'data_url': str, 'timestamp': float } }
CACHE_TTL = 60 * 60  # 1 hour

@app.route('/api/mangacover')
def mangacover():
    cover_id = request.args.get('cover','')
    manga_id = request.args.get('id','')
    if not cover_id or not manga_id:
        return jsonify({'url': None}), 400



    cache_key = f"{manga_id}_{cover_id}"
    now = time.time()

    # Check cache
    if cache_key in cache:
        cached = cache[cache_key]
        if now - cached['timestamp'] < CACHE_TTL:
            return jsonify({'url': cached['data_url']})

    print('making request to mangaddex')
    # Fetch cover info from MangaDex
    response = requests.get(f'https://api.mangadex.org/cover/{cover_id}')
    if response.status_code != 200:
        return jsonify({'error': 'Cover not found'}), 404

    data = response.json()
    file_name = data['data']['attributes']['fileName']

    # Construct full image URL
    image_url = f'https://uploads.mangadex.org/covers/{manga_id}/{file_name}'

    # Fetch the actual image bytes
    image_resp = requests.get(image_url)
    if image_resp.status_code != 200:
        return jsonify({'url': image_url})

    # Convert to base64
    encoded_image = base64.b64encode(image_resp.content).decode('utf-8')

    # Determine MIME type from file extension
    ext = file_name.split('.')[-1].lower()
    mime_type = 'image/png' if ext == 'png' else 'image/jpeg'

    data_url = f'data:{mime_type};base64,{encoded_image}'
    # Store in cache
    cache[cache_key] = {'data_url': data_url, 'timestamp': now}
    # Return as JSON
    return jsonify({'url': data_url})





if __name__ == "__main__":
    app.run(debug=True)

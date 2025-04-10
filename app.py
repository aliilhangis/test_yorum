from flask import Flask, request, jsonify, render_template
from google_play_scraper import reviews_all
import requests

app = Flask(__name__)

# App Store yorumlarını çek
def get_app_store_reviews(app_id):
    url = f'https://itunes.apple.com/rss/customerreviews/id={app_id}/sortBy=mostRecent/json'
    response = requests.get(url)
    
    try:
        data = response.json()
        reviews = data.get("feed", {}).get("entry", [])[1:]  # İlk entry app info oluyor
        filtered = [
            {
                "yorum": r.get("content", {}).get("label", ""),
                "puan": r.get("im:rating", {}).get("label", ""),
                "tarih": r.get("updated", {}).get("label", ""),
                "yazar": r.get("author", {}).get("name", {}).get("label", "")
            }
            for r in reviews if r.get("im:rating", {}).get("label") in ["1", "2", "3"]
        ]
        return filtered
    except Exception as e:
        return [{"error": f"App Store verisi alınamadı: {str(e)}"}]

# Play Store yorumlarını çek
def get_play_store_reviews(package_name):
    try:
        all_reviews = reviews_all(package_name)
        filtered = [
            {
                "yorum": r["content"],
                "puan": r["score"],
                "tarih": r["at"].strftime("%Y-%m-%d %H:%M:%S"),
                "yazar": r["userName"]
            }
            for r in all_reviews if r["score"] in [1, 2, 3]
        ]
        return filtered
    except Exception as e:
        return [{"error": f"Play Store verisi alınamadı: {str(e)}"}]

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

# Sonuç sayfası
@app.route('/get_reviews', methods=['POST'])
def get_reviews():
    app_store_id = request.form.get('app_store_id')
    play_store_package = request.form.get('play_store_package')

    results = {}

    if app_store_id:
        results["app_store"] = get_app_store_reviews(app_store_id)

    if play_store_package:
        results["play_store"] = get_play_store_reviews(play_store_package)

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)

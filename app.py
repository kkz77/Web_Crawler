from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
from scraper.scraper import scrape_players


app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "players.json")

def load_players():
    """Load players from JSON file"""
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def extract_country(place_of_birth):
    """Extracts the last word after the last comma to get the country name."""
    return place_of_birth.split(",")[-1].strip()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        num_players = int(request.form.get('num_players', 100))  # Default is 100
        scrape_players(num_players)  # Run scraper with user-defined limit
        return redirect(url_for('index'))  # Reload the page with updated data
    
    players = load_players()
    per_page = 8
    page = request.args.get('page', 1, type=int)
    selected_country = request.args.get('country', "All")

    # Extract unique country names
    countries = sorted(set(extract_country(player["place_of_birth"]) for player in players))

    # Filter players by selected country
    if selected_country and selected_country != "All":
        filtered_players = [p for p in players if extract_country(p["place_of_birth"]) == selected_country]
    else:
        filtered_players = players

    start = (page - 1) * per_page
    end = start + per_page
    total_pages = -(-len(filtered_players) // per_page)  # Calculate total pages

    return render_template('index.html', players=filtered_players[start:end], page=page, total_pages=total_pages, countries=countries, selected_country=selected_country)

@app.route('/scrape', methods=['POST'])
def scrape():
    """Handle AJAX request to scrape players dynamically."""
    try:
        data = request.get_json()
        num_players = int(data.get('num_players', 100))  # Default to 100
        scrape_players(num_players)
        return jsonify({"message": "Scraping completed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

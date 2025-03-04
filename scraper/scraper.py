import requests
import re
import json
import os
from time import sleep
from html import unescape
from flask import request

DELAY = 1  # Delay between requests

# Define the data path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "players.json")

def get_players_list(player_limit=100):
    """Fetches player list from Wikipedia based on user input."""
    main_url = 'https://en.wikipedia.org/wiki/List_of_Premier_League_winning_players'
    response = requests.get(main_url)
    html = response.text

    tables = re.findall(r'<table class="wikitable sortable plainrowheaders">(.*?)</table>', html, re.DOTALL)
    if not tables:
        print("No tables found on the page.")
        return []

    players = []
    for table in tables:
        rows = re.findall(r'<tr>(.*?)</tr>', table, re.DOTALL)
        for row in rows[1:]:  # Skip header row
            if len(players) >= player_limit:  # Stop when reaching limit
                break
            th_match = re.search(r'<th scope="row".*?<a href="(/wiki/[^"]+)"[^>]*>([^<]+)</a>', row, re.DOTALL)
            if th_match:
                href = th_match.group(1)
                name = th_match.group(2)
                full_url = f'https://en.wikipedia.org{href}'
                players.append({'name': name, 'url': full_url})
    return players

def get_player_info(player_url):
    """Extracts player details from Wikipedia."""
    try:
        response = requests.get(player_url)
        html = response.text

        infobox_match = re.search(r'<table class="infobox[^"]*"(.*?)</table>', html, re.DOTALL)
        if not infobox_match:
            print(f"No infobox found for {player_url}")
            return None
        infobox_html = infobox_match.group(0)
        print(infobox_html)

        full_name = re.search(r'<th scope="row" class="infobox-label".*?>Full name</th>\s*<td[^>]*>(.*?)<', infobox_html, re.DOTALL)
        date_of_birth = re.search(r'<th scope="row" class="infobox-label".*?>Date of birth</th>\s*<td[^>]*>.*?(\d{1,2}\s\w+\s\d{4})<', infobox_html, re.DOTALL) 
        place_of_birth = re.search(r'<th scope="row" class="infobox-label".*?>Place of birth</th>\s*<td[^>]*>(.*?)</td>', infobox_html, re.DOTALL) 
        height = re.search(r'<th scope="row" class="infobox-label".*?>Height</th>\s*<td[^>]*>(.*?)<', infobox_html, re.DOTALL) 
        position  = re.search(r'<th scope="row" class="infobox-label".*?>Position\(s\)</th>\s*<td[^>]*>.*?>(.*?)<', infobox_html, re.DOTALL) 
        img = re.search(r'<img\s+[^>]*src="([^"]+)"',infobox_html,re.DOTALL)

        full_name = full_name.group(1).strip()
        date_of_birth = date_of_birth.group(1).strip()
        place_of_birth = place_of_birth.group(1)
        place_of_birth = re.sub(r'<[^>]+>', '', unescape(place_of_birth))
        place_of_birth = re.sub(r'\[\d+\]', '', place_of_birth)
        place_of_birth = re.sub(r'\)$', '', place_of_birth)  
        place_of_birth = place_of_birth.strip()
        height = height.group(1).strip()
        height = re.sub(r'&#160;', ' ', height).strip()
        position = position.group(1).strip()
        img = "https:"+img.group(1)

        return {
            'full_name' : full_name,
            'date_of_birth' : date_of_birth,
            'place_of_birth' : place_of_birth,
            'height' : height,
            'position' : position,
            'img' : img  
        } 
    except Exception as e:
        print(f"Error processing {player_url}: {e}")
        return None

def scrape_players(player_limit=100):
    """Runs the scraper and saves data to JSON."""
    players = get_players_list(player_limit)
    if not players:
        return []

    data = []
    for player in players:
        print(f"Scraping {player['name']}...")
        info = get_player_info(player['url'])
        if info:
            data.append({**player, **info})

    # Save to JSON
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    return data

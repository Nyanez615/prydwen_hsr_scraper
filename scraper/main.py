# scraper/main.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

from scraper.db import SessionLocal, init_db
from scraper.models import Character
from sqlalchemy.exc import IntegrityError

import json
import csv
import os

def parse_rating(rating_str):
    """
    Remove 'T' and convert to float. 
    If rating_str == 'N/A' or cannot be parsed, return None.
    Example: 'T0' -> 0.0, 'T1.5' -> 1.5
    """
    if rating_str.upper().startswith('T'):
        rating_str = rating_str[1:]  # Remove leading 'T'
    rating_str = rating_str.strip()

    # If rating_str is "N/A" or empty, return None
    if rating_str.upper() == 'N/A' or not rating_str:
        return None
    
    # Attempt to parse as float
    try:
        return float(rating_str)
    except ValueError:
        return None

def scrape_star_rail_characters(limit=None):
    """
    Scrapes Star Rail character data from Prydwen.gg.
    :param limit: number of character cards to process (int)
    :return: list of dicts containing scraped character data
    """

    # -- HEADLESS CHROME SETUP --
    chrome_options = Options()
    chrome_options.add_argument("--headless")           # Run in headless mode
    chrome_options.add_argument("--disable-gpu")        # Disable GPU (best practice)
    chrome_options.add_argument("--no-sandbox")         # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource in Docker
    # Additional recommended options can be added as needed

    driver = webdriver.Chrome(options=chrome_options)
    characters = []

    try:
        driver.get("https://www.prydwen.gg/star-rail/characters/")

        # Wait for the cards to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "avatar-card"))
        )

        character_cards = driver.find_elements(By.CLASS_NAME, "avatar-card")
        actions = ActionChains(driver)

        possible_roles = ['DPS', 'Support DPS', 'Amplifier', 'Sustain']

        for card in character_cards[:limit]:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
            time.sleep(1)

            # Hover to trigger the popover
            actions.move_to_element(card).perform()
            time.sleep(1)

            try:
                popover_content = driver.find_element(By.CLASS_NAME, "tippy-content")
                soup = BeautifulSoup(popover_content.get_attribute('innerHTML'), 'html.parser')

                images = soup.find_all('img')
                if len(images) < 8:
                    # not enough info, skip
                    continue

                name = images[1]['alt']
                element = images[4]['alt']
                path = images[7]['alt']

                # Rarity
                if soup.find(class_='rar-5'):
                    rarity = '5★'
                elif soup.find(class_='rar-4'):
                    rarity = '4★'
                else:
                    rarity = 'Unknown'

                # Role
                text_content = soup.get_text(separator=' ')
                role = 'Unknown'
                for r in possible_roles:
                    if r in text_content:
                        role = r
                        break

                # Ratings
                moc_rating_str, pf_rating_str, as_rating_str = 'N/A', 'N/A', 'N/A'
                rating_divs = soup.find_all('div', class_=re.compile(r'rating-hsr-\d+'))

                if rating_divs:
                    if rarity == '5★':
                        # For 5★ characters, first 3 ratings
                        if len(rating_divs) >= 3:
                            moc_rating_str = rating_divs[0].get_text(strip=True)
                            pf_rating_str = rating_divs[1].get_text(strip=True)
                            as_rating_str = rating_divs[2].get_text(strip=True)
                    elif rarity == '4★':
                        # For 4★ characters, last 3 ratings (E6)
                        if len(rating_divs) >= 6:
                            moc_rating_str = rating_divs[3].get_text(strip=True)
                            pf_rating_str = rating_divs[4].get_text(strip=True)
                            as_rating_str = rating_divs[5].get_text(strip=True)

                # Convert to floats
                moc_rating_val = parse_rating(moc_rating_str)
                pf_rating_val = parse_rating(pf_rating_str)
                as_rating_val = parse_rating(as_rating_str)

                # Compute average (ignore None values by treating them as 0)
                numeric_ratings = [r for r in (moc_rating_val, pf_rating_val, as_rating_val) if r is not None]
                if numeric_ratings:
                    avg_rating = sum(numeric_ratings) / len(numeric_ratings)
                else:
                    avg_rating = None

                characters.append({
                    'name': name,
                    'element': element,
                    'path': path,
                    'rarity': rarity,
                    'role': role,
                    'moc_rating': moc_rating_val,
                    'pf_rating': pf_rating_val,
                    'as_rating': as_rating_val,
                    'average_rating': avg_rating,
                })

            except Exception as e:
                print(f"Error processing card: {e}")

    finally:
        driver.quit()

    return characters

def save_characters_to_db(characters):
    """
    Persists scraped character data into the database.
    """
    db = SessionLocal()
    try:
        for data in characters:
            char = Character(
                name=data['name'],
                element=data['element'],
                path=data['path'],
                rarity=data['rarity'],
                role=data['role'],
                moc_rating=data['moc_rating'],
                pf_rating=data['pf_rating'],
                as_rating=data['as_rating'],
                average_rating=data['average_rating']
            )
            db.add(char)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                print(f"Character '{char.name}' already exists. Skipping...")
    finally:
        db.close()

def get_characters():
    db = SessionLocal()
    try:
        all_chars = db.query(Character).all()
        return all_chars
    finally:
        db.close()

def export_characters_json(characters, filename="characters_export.json"):
    data = []
    for char in characters:
        data.append({
            "name": char.name,
            "element": char.element,
            "path": char.path,
            "rarity": char.rarity,
            "role": char.role,
            "moc_rating": char.moc_rating,
            "pf_rating": char.pf_rating,
            "as_rating": char.as_rating,
            "average_rating": char.average_rating
        })

    os.makedirs("data_exports", exist_ok=True)
    with open(os.path.join("data_exports", filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Exported {len(data)} records to {filename} successfully!")

def export_characters_csv(characters, filename="characters_export.csv"):
    os.makedirs("data_exports", exist_ok=True)
    with open(os.path.join("data_exports", filename), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name", "element", "path", "rarity", "role",
            "moc_rating", "pf_rating", "as_rating", "average_rating"
        ])
        for char in characters:
            writer.writerow([
                char.name,
                char.element,
                char.path,
                char.rarity,
                char.role,
                char.moc_rating,
                char.pf_rating,
                char.as_rating,
                char.average_rating
            ])
    print(f"Exported {len(characters)} records to {filename} successfully!")

def main():
    # Init DB
    init_db()

    # Scrape
    characters = scrape_star_rail_characters()

    # Save to DB
    if characters:
        save_characters_to_db(characters)

    print("Scraping and saving completed!")

    # Query all characters in DB
    all_chars = get_characters()

    # Export
    export_characters_json(all_chars, "characters.json")
    export_characters_csv(all_chars, "characters.csv")

if __name__ == "__main__":
    main()
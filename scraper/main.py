# scraper/main.py

from selenium import webdriver
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
import os

def scrape_star_rail_characters(limit=None):
    """
    Scrapes Star Rail character data from Prydwen.gg.
    :return: list of dicts containing scraped character data
    """
    driver = webdriver.Safari()
    characters = []

    try:
        # Navigate
        driver.get("https://www.prydwen.gg/star-rail/characters/")

        # Wait for cards to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "avatar-card"))
        )

        # Find all cards
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
                if len(images) >= 8:
                    name = images[1]['alt']
                    element = images[4]['alt']
                    path = images[7]['alt']

                    # Determine rarity
                    if soup.find(class_='rar-5'):
                        rarity = '5★'
                    elif soup.find(class_='rar-4'):
                        rarity = '4★'
                    else:
                        rarity = 'Unknown'

                    # Determine role
                    text_content = soup.get_text(separator=' ')
                    role = 'Unknown'
                    for r in possible_roles:
                        if r in text_content:
                            role = r
                            break

                    # Ratings
                    moc_rating, pf_rating, as_rating = 'N/A', 'N/A', 'N/A'
                    rating_divs = soup.find_all('div', class_=re.compile(r'rating-hsr-\d+'))

                    if rating_divs:
                        if rarity == '5★':
                            if len(rating_divs) >= 3:
                                moc_rating = rating_divs[0].get_text(strip=True)
                                pf_rating = rating_divs[1].get_text(strip=True)
                                as_rating = rating_divs[2].get_text(strip=True)
                        elif rarity == '4★':
                            if len(rating_divs) >= 6:
                                moc_rating = rating_divs[3].get_text(strip=True)
                                pf_rating = rating_divs[4].get_text(strip=True)
                                as_rating = rating_divs[5].get_text(strip=True)

                    characters.append({
                        'name': name,
                        'rarity': rarity,
                        'element': element,
                        'path': path,
                        'role': role,
                        'moc_rating': moc_rating,
                        'pf_rating': pf_rating,
                        'as_rating': as_rating
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
                rarity=data['rarity'],
                element=data['element'],
                path=data['path'],
                role=data['role'],
                moc_rating=data['moc_rating'],
                pf_rating=data['pf_rating'],
                as_rating=data['as_rating'],
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

def export_to_json(characters, filename="prydwen_hsr.json"):
    # Convert each SQLAlchemy object into a dict
    data = []
    for char in characters:
        data.append({
            "name": char.name,
            "rarity": char.rarity,
            "element": char.element,
            "path": char.path,
            "role": char.role,
            "moc_rating": char.moc_rating,
            "pf_rating": char.pf_rating,
            "as_rating": char.as_rating,
        })

    with open(os.path.join("data_exports", filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Exported {len(data)} records to {filename} successfully!")

import csv

def export_to_csv(characters, filename="prydwen_hsr.csv"):
    with open(os.path.join("data_exports", filename), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(["name", "rarity", "element", "path", "role", "moc_rating", "pf_rating", "as_rating"])

        for char in characters:
            writer.writerow([
                char.name,
                char.rarity,
                char.element,
                char.path,
                char.role,
                char.moc_rating,
                char.pf_rating,
                char.as_rating # Store JSON as string
            ])

    print(f"Exported {len(characters)} records to {filename} successfully!")

# def main():
#     characters = scrape_star_rail_characters()
#     # For now, just print them
#     for c in characters:
#         print(c)

def main():
    # 1. Initialize DB
    init_db()

    # 2. Scrape
    characters = scrape_star_rail_characters()
    if characters:
        # 3. Store in DB
        save_characters_to_db(characters)

    print("Scraping and saving completed!")

    # Query all characters in DB
    all_characters = get_characters()

    # Export
    export_to_json(all_characters, "characters_export.json")
    export_to_csv(all_characters, "characters_export.csv")

if __name__ == "__main__":
    main()

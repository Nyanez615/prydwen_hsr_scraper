# scraper/main.py

from scraper.db import SessionLocal, init_db
from scraper.models import Character
from sqlalchemy.exc import IntegrityError
import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

def scrape_star_rail_characters():
    # Initialize Safari WebDriver
    driver = webdriver.Safari()

    characters = []

    try:
        # Navigate to the Prydwen.gg Star Rail characters page
        driver.get("https://www.prydwen.gg/star-rail/characters/")

        # Wait until the character cards are loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "avatar-card"))
        )

        # Find all character cards
        character_cards = driver.find_elements(By.CLASS_NAME, "avatar-card")

        # Initialize ActionChains
        actions = ActionChains(driver)

        # Define possible roles
        possible_roles = ['DPS', 'Support DPS', 'Amplifier', 'Sustain']

        # Iterate over the character cards (adjust as needed)
        for card in character_cards:
            # Scroll the character card into view
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", 
                card
            )
            time.sleep(1)  # Allow time for scrolling animation

            # Hover over the character card to trigger the popover
            actions.move_to_element(card).perform()
            time.sleep(1)  # Wait for the popover to appear

            # Locate the popover content
            try:
                popover_content = driver.find_element(
                    By.CLASS_NAME, 
                    "tippy-content"
                )
                # Parse the popover content with BeautifulSoup
                soup = BeautifulSoup(
                    popover_content.get_attribute('innerHTML'),
                    'html.parser'
                )

                # Extract all image tags
                images = soup.find_all('img')
                if len(images) >= 8:
                    name = images[1]['alt']
                    element = images[4]['alt']
                    path = images[7]['alt']

                    # Determine rarity based on CSS class
                    if soup.find(class_='rar-5'):
                        rarity = '5★'
                    elif soup.find(class_='rar-4'):
                        rarity = '4★'
                    else:
                        rarity = 'Unknown'

                    # Extract text content to find the role
                    text_content = soup.get_text(separator=' ')
                    role = 'Unknown'
                    for r in possible_roles:
                        if r in text_content:
                            role = r
                            break

                    # Extract ratings
                    ratings = {'MoC': 'N/A', 'PF': 'N/A', 'AS': 'N/A'}
                    # Find all divs with class names matching 'rating-hsr-#'
                    rating_divs = soup.find_all(
                        'div',
                        class_=re.compile(r'rating-hsr-\d+')
                    )

                    if rating_divs:
                        if rarity == '5★':
                            # For 5★ characters, use the first three ratings
                            if len(rating_divs) >= 3:
                                ratings['MoC'] = rating_divs[0].get_text(strip=True)
                                ratings['PF'] = rating_divs[1].get_text(strip=True)
                                ratings['AS'] = rating_divs[2].get_text(strip=True)
                        elif rarity == '4★':
                            # For 4★ characters, use the last three ratings (E6)
                            if len(rating_divs) >= 6:
                                ratings['MoC'] = rating_divs[3].get_text(strip=True)
                                ratings['PF'] = rating_divs[4].get_text(strip=True)
                                ratings['AS'] = rating_divs[5].get_text(strip=True)

                    characters.append({
                        'name': name,
                        'element': element,
                        'path': path,
                        'rarity': rarity,
                        'role': role,
                        'ratings': ratings
                    })

            except Exception as e:
                print(f"Error processing card: {e}")

    finally:
        # Close the WebDriver
        driver.quit()

    return characters

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
            "element": char.element,
            "path": char.path,
            "rarity": char.rarity,
            "role": char.role,
            "ratings": char.ratings
        })

    with open(os.path.join("data_exports", filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Exported {len(data)} records to {filename} successfully!")

import csv

def export_to_csv(characters, filename="prydwen_hsr.csv"):
    with open(os.path.join("data_exports", filename), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(["name", "element", "path", "rarity", "role", "ratings"])

        for char in characters:
            writer.writerow([
                char.name,
                char.element,
                char.path,
                char.rarity,
                char.role,
                json.dumps(char.ratings)  # Store JSON as string
            ])

    print(f"Exported {len(characters)} records to {filename} successfully!")

# def main():
#     characters = scrape_star_rail_characters()
#     # For now, just print them
#     for c in characters:
#         print(c)

def main():
    # 1. Initialize the database (creates tables if not exist)
    init_db()

    # 2. Scrape the characters
    characters = scrape_star_rail_characters()

    # 3. Save them to the database
    db = SessionLocal()
    try:
        for char_data in characters:
            char = Character(
                name=char_data['name'],
                element=char_data['element'],
                path=char_data['path'],
                rarity=char_data['rarity'],
                role=char_data['role'],
                ratings=char_data['ratings']  # This is a dict
            )
            db.add(char)
            try:
                db.commit()
            except IntegrityError:
                # If character name is already in the database, 
                # we can decide whether to update or skip
                db.rollback()
                print(f"Character {char.name} already exists, skipping...")

    finally:
        db.close()

    print("Characters added to the database successfully!")

    # Query all characters in DB
    all_characters = get_characters()

    # Export
    export_to_json(all_characters, "characters_export.json")
    export_to_csv(all_characters, "characters_export.csv")

if __name__ == "__main__":
    main()

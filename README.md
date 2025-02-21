# Star Rail Scraper

This scraper collects character data from [Prydwen.gg](https://www.prydwen.gg/star-rail/characters/) for the game Honkai: Star Rail.

## Features
- Selenium-based web scraping
- SQLite database storage (via SQLAlchemy)
- JSON/CSV exports
- Easy to query local database

## Setup & Usage
1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the scraper: 
    ```bash
    python -m scraper.main
    ```
- This will scrape data, store it in star_rail.db, and generate exports in data_exports/.

## Contributing 
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

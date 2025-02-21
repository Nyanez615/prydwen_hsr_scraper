# Star Rail Scraper

A Python-based scraper for [Prydwen.gg](https://www.prydwen.gg/star-rail/characters/) to collect Honkai: Star Rail character data, including **numeric ratings** and an **average rating** (rounded to 2 decimals).

## Features

- Uses **Selenium** (headless browser) to parse data
- Separate columns for MoC, PF, and AS ratings (float) plus an **average_rating**
- **Environment variables** to control DB path, browser choice, scrape URL, etc.
- Robust **explicit waits** instead of `time.sleep()`
- **Logging** via Python's `logging` module
- GitHub Actions: 
  - **CI** for tests  
  - **Scheduled** daily run that uploads the latest `hsr.db` artifact

## Installation

1. **Clone** this repository:
   
   ```bash
   git clone https://github.com/YourUsername/star-rail-scraper.git
   cd star-rail-scraper
   ```

2. **Create and activate** a virtual environment
   
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
- (On Windows, use `venv\Scripts\activate`.)

3. Install dependencies:
   
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Usage

1. Set environment variables (optional):
   
   ```bash
   export BROWSER=chromium        # or "chrome" or "firefox"
   export SCRAPE_URL="https://www.prydwen.gg/star-rail/characters/"
   export SCRAPE_LIMIT=None
   export DB_URL="sqlite:///hsr.db"  # Or your own DB location
   ```

- Defaults:
  - BROWSER=`chromium`
  - SCRAPE_URL=`https://www.prydwen.gg/star-rail/characters/`
  - SCRAPE_LIMIT=`None`
  - DB_URL=`sqlite:///hsr.db`

2. Run the scraper: 
   
   ```bash
   python -m scraper.main
   ```

- This will launch headless Chrome (or the chosen browser), scrape all characters, store them in `hsr.db`, and log progress to the console.

## Testing

- We use pytest for testing:
   
   ```bash
   pytest
   ```

## GitHub Actions

- CI: `.github/workflows/ci.yml`
  - Runs tests on every push or pull request.
- Scheduled Scraper: `.github/workflows/schedule.yml`
  - Runs daily at 2 AM UTC, executes `python -m scraper.main`, and uploads `hsr.db`, `characters.json`, and `characters.csv` as artifacts.

## Additional Configuration

- See `scraper/config.py` for browser-specific options.
- If you need to customize the logging format or level, edit `logging.basicConfig` in `scraper/main.py`.

## Contributing 

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

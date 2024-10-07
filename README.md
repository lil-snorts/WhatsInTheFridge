# WebCrawler with Persistence for Recipe Scraping

This repository contains a Python-based web crawler designed to scrape recipe ingredients from the "AllRecipes" website. It incorporates persistence features, allowing the program to store scraped data in a CSV file and avoid revisiting previously scraped pages. This project is built using `requests`, `BeautifulSoup`, and `pandas` libraries, ensuring robust and efficient web crawling and data management.

## Features

- **Crawling & Scraping**: The web crawler navigates through recipe links on the site and extracts ingredients using specific HTML tags.
- **Persistence Management**: A CSV file is used to store the URLs and corresponding ingredient data, avoiding re-scraping of already processed pages.
- **Robots.txt Handling**: The crawler respects site restrictions as defined in the `robots.txt` file, ensuring compliance with web scraping guidelines.
- **CSV Output**: The ingredients data for each recipe is stored in a CSV file, with rows representing URLs and columns representing ingredients.
- **Resume Scraping**: If a crawl is interrupted or already scraped, the program can resume from the last checkpoint using the data saved in the CSV file.

## Prerequisites

Before running the project, ensure you have the following Python packages installed:

- `requests`
- `pandas`
- `beautifulsoup4`

You can install the required dependencies using:

```bash
pip install requests beautifulsoup4 pandas
```

## Project Structure

- **WebCrawlerPersistenceManager**: Manages reading and writing to a CSV file. This ensures the crawler doesn't revisit previously scraped URLs and provides a way to persist the data for future analysis.
- **AllRecipesWebCrawler**: Contains the logic for fetching pages, parsing HTML, extracting ingredient data, and navigating between recipe links.

## Usage

1. **Download The Repo**: To download the repo, clone it to your machine
   ```bash
   git clone https://github.com/lil-snorts/WhatsInTheFridge.git
   cd WhatsInTheFridge
   ```
1. **Configure Settings**: Update the constants (base URL, starting URL, robots.txt link, and HTML target elements) in the `if __name__ == "__main__":` section.
   
2. **Run the Crawler**:

   You can start the web crawling process by running:

   ```bash
   python3 py/src/all_recipe_scraper.py
   ```

   The crawler will:
   - Read previously scraped data from `recipes.csv` (if available).
   - Fetch new pages, scrape ingredients, and store the data in the CSV file.
   - Respect the rules defined in the `robots.txt` file.

3. **Data Output**: After crawling, a CSV file (`recipes.csv`) will be generated containing the scraped data. The file includes URLs as rows and ingredients as columns, with an 'Y' denoting the presence of an ingredient for each recipe.

## Example Output

The CSV file will have a structure like this:

| url                                | salt | sugar | pepper | ... |
|-------------------------------------|------|-------|--------|-----|
| https://www.allrecipes.com/recipe/1 | Y    | Y     | Y      | ... |
| https://www.allrecipes.com/recipe/2 | Y    |       | Y      | ... |

## Handling Interruptions

In the event of an interruption (e.g., keyboard interrupt), the crawler will save the currently scraped data and allow you to resume from where you left off.

## Contributing

Contributions are welcome! If you have suggestions for improvements or find any bugs, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
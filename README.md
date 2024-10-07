# Simple Web Crawler for Recipe Extraction

This repository contains a Python script that implements a basic web crawler designed to scrape recipe information from a website, specifically extracting ingredients from recipe pages and storing them in a CSV file. The script uses various Python libraries such as `requests`, `BeautifulSoup`, and `pandas` to achieve this goal.

## Features
- **Web Crawling**: Extracts data from web pages starting from a given URL, following hyperlinks recursively.
- **Robots.txt Respect**: The crawler parses and respects the `robots.txt` file of the target site to avoid crawling restricted pages.
- **Ingredient Extraction**: Specifically targets pages containing recipe ingredients, identified through a specific HTML tag structure.
- **Persistence**: Utilizes a CSV file to store and reload previously scraped results, preventing redundant scraping and improving efficiency.
- **Customizable**: Easily adaptable to different websites by changing the base URL, data extraction logic, and crawling rules.

## Installation

To use the web crawler, ensure you have Python 3.6+ installed. You also need the following libraries, which you can install using `pip`:

```bash
pip install requests beautifulsoup4 pandas
```

## Usage

1. Clone the repository:

```bash
git clone https://github.com/your-username/web-crawler-recipe.git
cd web-crawler-recipe
```

2. Ensure that the URLs in the script are valid for your target website, specifically the following variables:

```python
baseSite = "https://www.allrecipes.com/recipe"
start_url = "https://www.allrecipes.com/recipes-a-z-6735880"
robots_txt = "https://www.allrecipes.com/robots.txt"
```

3. Run the script:

```bash
python crawler.py
```

The crawler will start fetching recipe information, extracting ingredients, and storing the results in `recipes.csv`.

### Script Breakdown

#### Classes:

1. **`WebCrawlerPersistenceManager`**:  
   Handles saving the scraped data into a CSV file and loading previously scraped data to avoid redundant requests.
   
   - `readPreviousScrape()`: Reads from an existing CSV and loads scraped data.
   - `writeToCsv(data: dict)`: Writes scraped data (recipe URLs and ingredients) into a CSV file.
   
2. **`SimpleWebCrawler`**:  
   The core crawler class, responsible for managing the crawling process, fetching web pages, and extracting useful information.

   - `fetch_page(url)`: Fetches a web page's content.
   - `setRules(forbidden_robots_txt_link)`: Parses the `robots.txt` file and sets disallowed patterns for URLs.
   - `parse_page(html_content)`: Uses BeautifulSoup to parse the HTML content of a page.
   - `extract_links(soup, base_url)`: Extracts all valid hyperlinks from the parsed page.
   - `crawl(url)`: Recursively crawls the website, collecting recipe information.
   - `start_crawl()`: Begins the crawling process.

### Example Output
The results are stored in `recipes.csv` with columns representing URLs and the corresponding ingredients found on each page. Each row corresponds to a recipe URL, with ingredient presence marked as "Y" (Yes).

```csv
url,ingredient_1,ingredient_2,...
https://www.allrecipes.com/recipe/1,Y,,Y,...
https://www.allrecipes.com/recipe/2,Y,Y,Y,...
```

## Customization
To adapt this crawler for a different website:
- Modify the `baseSite` and `start_url` variables to point to the desired domain.
- Adjust the `parse_page` method to identify and extract the necessary content from the new website’s HTML structure.

## Known Limitations
- **Limited Domain Crawling**: The script is hardcoded to crawl pages within the `baseSite` domain.
- **Robustness**: This is a simple implementation that might fail if the target site structure changes significantly.
- **Politeness**: Although it reads and respects `robots.txt`, the crawler does not implement rate-limiting or delay mechanisms, which may result in a high load on the target server.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For any inquiries or suggestions, feel free to reach out via [your-email@example.com].

---

This script is ideal for anyone interested in basic web scraping, building datasets from online resources, or learning how to manage web crawling rules using Python.

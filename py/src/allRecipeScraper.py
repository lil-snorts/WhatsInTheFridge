import requests
import re as regex
import pandas as pd
from bs4 import BeautifulSoup



# Abstract Persistence Manager for the WebCrawler 
# Allows for writing results of a webcrawl to a CSV
# Allows for pre-population of a webcrawl by reading from a CSV
# Saves time by not re-visiting previously explored Webpages
# Save data that could be used for statistical analysis 
class WebCrawlerPersistenceManager:
    _FILE_NAME = "recipes.csv"
    _URL_KEY = "url"
    
    def readPreviousScrape(self) -> dict[str, list[str]]:
        try:
            df = pd.read_csv(self._FILE_NAME, index_col=0)
            
            previousScrape: dict[str, list[str]] = {}
            
            # create a url to ingredients map 
            for row in df.itertuples(True, "row"):
                
                row_data = []
                
                for x in range(1, len(row) - 1):
                    if row[x] == "Y":
                        row_data.append(df.columns.array[x])

                previousScrape[row[0]] = row_data
            
            
            return previousScrape
        except Exception as e:
            print("Likely no previous scrape detected")
            print(e)
            return {}

    def writeToCsv(self, data: dict[str, list[str]]):
        
        headerSet = {self._URL_KEY: None}
        
        # The name of all the ingredients
        header_list: list[str] = [self._URL_KEY]
        
        # meta Info 
        totalItems = 0
        if len(data) == 0:
            return
        
        for _, data_row in data.items():
            for item in data_row:
                if item == "":
                    continue
                
                totalItems += 1
                if item not in headerSet:
                    headerSet[item] = 1
                    header_list.append(regex.sub(r"\W", "_", item))
        
        del headerSet
        
        # this are our csv file headers
        print(header_list)
        print(f'{len(header_list)} with {totalItems} total')
        
        # Create a list of dictionaries, mapping each row to its header
        rows: list[dict[str: str]] = []
        
        for url, ingredient_list in data.items():
            # Initialize a dictionary, eq to the size of the headers arr, with None for all headers
            row_dict: dict[str, str] = {header: None for header in header_list}  
            row_dict[self._URL_KEY] = url
            
            for ingredient in ingredient_list:
                sanitized_ingredient = regex.sub(r"\W", "_", ingredient)
                if sanitized_ingredient in header_list:
                    # Set the value to 'Y' for present ingredient
                    row_dict[sanitized_ingredient] = "Y"
                
            rows.append(row_dict)

        # Create DataFrame
        df = pd.DataFrame(rows, columns=header_list)
        df.set_index(self._URL_KEY, inplace=True)
        # Print the DataFrame
        print(df)
        
        df.to_csv(self._FILE_NAME)
        

class SimpleWebCrawler:
    class _RobotsParsingState:
        PRE_APPLICABLE = 0
        STARTED = 1
        FINISHED = 2
    
    def __init__(self, start_url):
        self.start_url = start_url
        self.forbidden_sites = []
        self.visited_urls = {}
        self.recipes: dict[str, list[str]] = {}       

    def fetch_page(self, url):
        print(f"fetching: {url}")
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"!\tError fetching {url}: {e}")
            return None
        
    def setRules(self, forbidden_robots_txt_link):
        
        state = self._RobotsParsingState.PRE_APPLICABLE
        
        # for each line after User-agent: * in the robots file, 
        # add each regex after "Disallow: " to an array of forbidden websites
        robot_page = self.fetch_page(forbidden_robots_txt_link)
        # print (robot_page)
        # https://docs.python.org/3/howto/regex.html
        # 
        # foreach badLink in the
        lines =  robot_page.split('\n')
        
        applicable_sites = []
        
        for line in lines:
            if (line == "User-agent: *"):
                state = self._RobotsParsingState.STARTED
            elif state == self._RobotsParsingState.STARTED:
                if "User-agent" in line:
                    state = self._RobotsParsingState.FINISHED
                elif line != "":
                    applicable_sites.append(line)
            elif state == self._RobotsParsingState.FINISHED:
                break

        allowed_patterns = []
        disallowed_patterns = []
        for siteRegex in applicable_sites:
            siteRegex = siteRegex.replace("*", ".*")
            
            if "Disallow" in siteRegex:
                filteredRegex = siteRegex.replace("Disallow: ", "")
                compiledRegex = regex.compile(filteredRegex)
                disallowed_patterns.append(compiledRegex)
            else:
                filteredRegex = siteRegex.replace("Allow: ", "")
                compiledRegex = regex.compile(filteredRegex)
                allowed_patterns.append(compiledRegex)
        
        self.forbidden_sites = disallowed_patterns
        return allowed_patterns, disallowed_patterns

    def parse_page(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup

    def extract_links(self, soup, base_url):
        links = set()
        for link in soup.find_all('a', href=True):
            full_url = requests.compat.urljoin(base_url, link['href'])
            if full_url not in self.visited_urls:
                links.add(full_url)
        return links

    def crawl(self, url):
        
        # So we don't visit the urls we've already visited
        if url in self.visited_urls or url in self.recipes:
            return
        
        # if the site isn't part of the site we want to scrape
        if baseSite not in url:
            print(f"!\tnot base site url: {url}")
            self.visited_urls[url] = ''
            return
        
        # If robots.txt forbids this pattern for exploitation
        for pattern in self.forbidden_sites:
            if pattern.match(url):
                print(f"forbidden url: {url}")
                self.visited_urls[url] = ''
                return

        
        html_content = self.fetch_page(url)
        
        if html_content is None:   
            self.visited_urls[url] = ''
            return

        soup = self.parse_page(html_content)
        
        ingredientsBody = soup.find_all("span", {"data-ingredient-name": "true"})
        
        ingredientsText = [itr.get_text().replace("\n", "").lower() for itr in ingredientsBody]
        
        if not ingredientsText:
            print("!\t no recipe")
            self.visited_urls[url] = ''
        else:
            print(f"+\tfound {len(ingredientsText)}")
            # write the output to a dict where the url is the key
            self.recipes.update({url: ingredientsText})
        
        links = self.extract_links(soup, url)

        # Here, you can add custom logic to extract data from the soup object
        # For example: extracting text, images, tables, etc.

        for link in links:
            self.crawl(link)

    def start_crawl(self):
        self.crawl(self.start_url)

if __name__ == "__main__":
    baseSite = "https://www.allrecipes.com/recipe"
    start_url = "https://www.allrecipes.com/recipes-a-z-6735880" 
    robots_txt = "https://www.allrecipes.com/robots.txt"
    crawler = SimpleWebCrawler(start_url)
    writer = WebCrawlerPersistenceManager()
    try:
        crawler.recipes = writer.readPreviousScrape()
        crawler.start_crawl()
    except Exception as e:
        print(e)
    finally:
        writer.writeToCsv(crawler.recipes)

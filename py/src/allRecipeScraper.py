import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

class RobotsParsingState:
    PRE_APPLICABLE = 0
    STARTED = 1
    FINISHED = 2

class DataReaderWriter:
    FILE_NAME = "recipies.csv"
    URL_KEY = "url"
    
    ## TODO abstract this so that it can be used abstractly
    # TODO I'm not quite sure how this will work if a new data point is added.
    # Might have to read into this via Pandas documentation
    def readPreviousScrape(self) -> dict[str, list[str]]:
        try:
            df = pd.read_csv(self.FILE_NAME)
            
            previousScrape: dict[str, list[str]] = {}
            
            # create a url to ingredients map 
            for itr in  df.itertuples():
                
                previousScrape[itr.index] = itr
            
            
            return previousScrape
        except Exception as e:
            print("Likely no previous scrape detected")
            return {}

        
    def writeToCsv(self, data: dict[str, list[str]]):
        
        headerSet = {self.URL_KEY: None}
        
        # The name of all the ingredients
        header_list: list[str] = [self.URL_KEY]
        
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
                    header_list.append(item.replace(" ", "_"))
        
        del headerSet
        
        # this are our csv file headers
        print(header_list)
        print(f'{len(header_list)} with {totalItems} total')
        
        # Create a list of dictionaries, mapping each row to its header
        rows: list[dict[str: str]] = []
        
        for url, ingredient_list in data.items():
            # Initialize a dictionary, eq to the size of the headers arr, with None for all headers
            row_dict: dict[str, str] = {header: None for header in header_list}  
            row_dict[self.URL_KEY] = url
            
            for ingredient in ingredient_list:
                if ingredient in header_list:
                    # Set the value to 'Y' for present ingredient
                    row_dict[ingredient] = "Y"
                
            rows.append(row_dict)

        # Create DataFrame
        df = pd.DataFrame(rows, columns=header_list)
        df.set_index(self.URL_KEY, inplace=True)
        # Print the DataFrame
        print(df)
        
        df.to_csv(self.FILE_NAME)
        
class SimpleWebCrawler:
    
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
        
    def setRules(self, fobidden_robots_txt_link):
        
        state = RobotsParsingState.PRE_APPLICABLE
        
        # for each line after User-agent: * in the robots file, 
        # add each regex after "Disallow: " to an array of forbidden websites
        robot_page = self.fetch_page(fobidden_robots_txt_link)
        # print (robot_page)
        # https://docs.python.org/3/howto/regex.html
        # 
        # foreach badLink in the
        lines =  robot_page.split('\n')
        
        applicable_sites = []
        
        for line in lines:
            if (line == "User-agent: *"):
                state = RobotsParsingState.STARTED
            elif state == RobotsParsingState.STARTED:
                if "User-agent" in line:
                    state = RobotsParsingState.FINISHED
                elif line != "":
                    applicable_sites.append(line)
            elif state == RobotsParsingState.FINISHED:
                break

        pprint(applicable_sites)
        
        allowed_patterns = []
        disallowed_patterns = []
        for siteRegex in applicable_sites:
            siteRegex = siteRegex.replace("*", ".*")
            
            if "Disallow" in siteRegex:
                filteredRegex = siteRegex.replace("Disallow: ", "")
                comiledRegex = re.compile(filteredRegex)
                disallowed_patterns.append(comiledRegex)
            else:
                filteredRegex = siteRegex.replace("Disallow: ", "")
                comiledRegex = re.compile(filteredRegex)
                allowed_patterns.append(comiledRegex)
        
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
        
        # So we don't visit the urls we've already visted
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
        
        ingredientsText = [itr.get_text().replace("\n", "") for itr in ingredientsBody]
        
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
    start_url = "https://www.allrecipes.com/recipes-a-z-6735880"  # Replace with your starting URL
    robots_txt = "https://www.allrecipes.com/robots.txt"
    # robots_txt = "https://discord.com/robots.txt"
    crawler = SimpleWebCrawler(start_url)
    writer = DataReaderWriter()
    try:
        crawler.recipes = writer.readPreviousScrape()
        crawler.start_crawl()
    except KeyboardInterrupt:
        for k, v in crawler.recipes.items():
            print(f"{k}: ")
            for itr in v:
                print(f"{itr}, ")
            print("\n")
    except Exception as e:
        print(e)
    finally:
        writer.writeToCsv(crawler.recipes)

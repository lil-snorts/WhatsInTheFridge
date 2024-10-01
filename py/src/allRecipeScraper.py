import requests
import re
import pandas as pd
import csv
from pprint import pprint 
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
    def readPreviousScrape(): list[str]
        df = pd.read_csv(self.FILE_NAME)
        
        previousScrape = df[self.URL_KEY].tolist()
        
        return previousScrape
        
    def write(self, data: dict[str, list[str]]):
        
        headerSet = {self.URL_KEY: None}
        headers = [self.URL_KEY]
        # Info 
        totalItems = 0
        
        for key, dataItems in data.items():
            for val in dataItems:
                if val is "":
                    continue
                
                totalItems+=1
                if val not in headerSet:
                    headerSet[val] = 1
                    headers.append(val)
        del headerSet
        
        # this are our csv file headers
        print(headers)
        print(f'{len(headers)} with {totalItems} total')
        # Create a list of dictionaries, mapping each row to its header
        rows = []
        for url, rowData in data.items():
            # Initialize a dictionary, eq to the size of the headers arr, with None for all headers
            row_dict = {header: 0 for header in headers}  
            row_dict[self.URL_KEY] = url    
            
            for elem in rowData:
                if elem in headers:
                    # Set the value to '1' for present elements
                    row_dict[elem] = 1
                
            rows.append(row_dict)

        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)

        # Print the DataFrame
        print(df)
        df.to_csv(self.FILE_NAME)
        
class SimpleWebCrawler:
    
    def __init__(self, start_url):
        self.start_url = start_url
        self.forbidden_sites = []
        self.visited_urls = {}
        self.recipies = {}       

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
        if url in self.visited_urls or url in self.recipies:
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
            self.recipies.update({url: ingredientsText})
        
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
    writer = DataWriter()
    pprint(crawler.setRules(robots_txt))
    try:
        crawler.start_crawl()
    except KeyboardInterrupt:
        for k, v in crawler.recipies.items():
            print(k+": ")
            for itr in v:
                print(f"{itr}, ")
            print("\n")
    finally:
        writer.write(crawler.recipies)

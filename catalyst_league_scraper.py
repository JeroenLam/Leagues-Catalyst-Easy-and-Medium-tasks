#!/usr/bin/env python3
"""
RuneScape Catalyst League Tasks Scraper

This script scrapes the RuneScape wiki page for Catalyst League tasks and exports
the data to a JSON file. It extracts Area, Task, Information, Requirements, and Pts
columns while handling images and HTML content appropriately.

Usage:
    python catalyst_league_scraper.py

Output:
    catalyst_league_tasks.json - UTF-8 encoded JSON file with task data

Requirements:
    - requests
    - beautifulsoup4
    - pandas (optional, for CSV fallback)

Author: Generated for RuneScape wiki scraping
"""

import requests
import csv
import json
import re
import time
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup, NavigableString
import html

# Try to import pandas, fall back to csv module if not available
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    pd = None
    HAS_PANDAS = False
    print("pandas not available, using csv module for output")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CatalystLeagueScraper:
    """Scraper for RuneScape Catalyst League tasks from wiki."""
    
    def __init__(self):
        self.url = "https://runescape.wiki/w/Catalyst_League/Tasks"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.data = []
        
    def fetch_page(self, retries=3, delay=1):
        """
        Fetch the webpage with error handling and retries.
        
        Args:
            retries (int): Number of retry attempts
            delay (int): Delay between retries in seconds
            
        Returns:
            requests.Response: The response object
            
        Raises:
            requests.RequestException: If all retry attempts fail
        """
        for attempt in range(retries + 1):
            try:
                logger.info(f"Fetching page... (attempt {attempt + 1}/{retries + 1})")
                response = self.session.get(self.url, timeout=30)
                response.raise_for_status()
                logger.info(f"Successfully fetched page. Content length: {len(response.content)} bytes")
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.error("All retry attempts failed")
                    raise
        
        # This should never be reached due to the raise above, but helps with type checking
        raise requests.exceptions.RequestException("Failed to fetch page after all retries")
    
    def clean_text(self, element):
        """
        Extract clean text from HTML element, removing all HTML tags and links.
        
        Args:
            element: BeautifulSoup element or string
            
        Returns:
            str: Cleaned text content
        """
        if element is None:
            return ""
            
        if isinstance(element, NavigableString):
            text = str(element)
        else:
            # Get text content, which automatically strips HTML tags
            text = element.get_text(separator=' ', strip=True)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_area_name(self, td_element):
        """
        Extract area name from the data-sort-value attribute of td element.
        
        Args:
            td_element: BeautifulSoup td element
            
        Returns:
            str: Area name or empty string if not found
        """
        if td_element and td_element.has_attr('data-sort-value'):
            return td_element['data-sort-value'].strip()
        return ""
    
    def extract_points(self, td_element):
        """
        Extract numerical points value from points column.
        
        Args:
            td_element: BeautifulSoup td element
            
        Returns:
            str: Points value or empty string
        """
        if not td_element:
            return ""
            
        text = self.clean_text(td_element)
        
        # Extract numbers from the text
        numbers = re.findall(r'\d+', text)
        if numbers:
            return numbers[0]  # Return first number found
        
        return ""
    
    def process_requirements(self, td_element):
        """
        Process requirements column, converting "N/A" to empty string.
        
        Args:
            td_element: BeautifulSoup td element
            
        Returns:
            str: Processed requirements text
        """
        text = self.clean_text(td_element)
        
        # Convert "N/A" to empty string
        if text.upper() == "N/A":
            return ""
            
        return text
    
    def generate_tags(self, task, information, requirements, area, pts):
        """
        Generate tags based on task content to help with categorization.
        
        Args:
            task (str): Task name
            information (str): Task information
            requirements (str): Task requirements
            area (str): Task area
            pts (str): Points value
            
        Returns:
            list: List of relevant tags
        """
        tags = []
        
        # Combine all text for analysis
        all_text = f"{task} {information} {requirements}".lower()
        
        # Difficulty tags based on points (primary indicator)
        if pts == '10':
            tags.append('Easy')
        elif pts == '30':
            tags.append('Medium')
        elif pts in ['50', '60', '100']:  # Hard tasks if they exist
            tags.append('Hard')
        
        # Special starting tasks
        if any(word in all_text for word in ['tutorial', 'leagues tutorial', 'first relic', 'skillguide']):
            tags.append('!Starting')
        
        # Skill-based tags (comprehensive list) - use word boundaries for exact matching
        skills = {
            'mining': r'\bmining\b',
            'smithing': r'\bsmithing\b',
            'fishing': r'\bfishing\b',
            'cooking': r'\bcooking\b',
            'woodcutting': r'\bwoodcutting\b',
            'firemaking': r'\bfiremaking\b',
            'crafting': r'\bcrafting\b',
            'fletching': r'\bfletching\b',
            'runecrafting': r'\brunecrafting\b',
            'construction': r'\bconstruction\b',
            'agility': r'\bagility\b',
            'herblore': r'\bherblore\b',
            'thieving': r'\bthieving\b',
            'slayer': r'\bslayer\b',
            'farming': r'\bfarming\b',
            'ranged': r'\branged\b',
            'prayer': r'\bprayer\b',
            'magic': r'\bmagic\b',
            'divination': r'\bdivination\b',
            'archaeology': r'\barchaeology\b',
            'hunter': r'\bhunter\b',
            'summoning': r'\bsummoning\b',
            'dungeoneering': r'\bdungeoneering\b',
            'necromancy': r'\bnecromancy\b',
            'attack': r'\battack\b',
            'strength': r'\bstrength\b',
            'defence': r'\bdefence\b'
        }
        
        import re
        for skill, pattern in skills.items():
            if re.search(pattern, all_text):
                tags.append(skill.title())
        
        # Special skill detection for activities that might not use exact skill names
        if any(word in all_text for word in ['memory', 'wisp', 'energy', 'enrich']):
            tags.append('Divination')
        
        # Activity-based tags - more comprehensive detection
        
        # Killing activities
        if any(word in all_text for word in ['kill', 'defeat', 'slay', 'combat']):
            tags.append('Killing')
        
        # Quest-related
        if any(word in all_text for word in ['quest', 'miniquest', 'complete this quest']):
            tags.append('Quest')
        
        # Diary/Achievement tasks
        if any(word in all_text for word in ['diary', 'achievement']):
            tags.append('Diary')
        
        # Exploration activities - be more specific to avoid false positives
        exploration_keywords = [
            'climb to the top', 'enter the', 'visit', 'activate the', 'talk to', 'explore',
            'activate.*lodestone', 'charter a ship', 'travel to', 'move your house',
            'teleport to', 'set sail', 'ride a', 'jump over', 'pass through'
        ]
        
        # Use regex for more precise matching
        for keyword in exploration_keywords:
            if re.search(keyword, all_text):
                tags.append('Exploration')
                break
        
        # Specific NPC interactions that count as exploration
        if any(phrase in all_text for phrase in ['have ned make', 'give thurgo', 'give bill']):
            tags.append('Exploration')
        
        # Banking/Shopping
        if any(word in all_text for word in ['bank', 'shop', 'store', 'buy', 'sell', 'claim a free item']):
            tags.append('Bank/Shop')
        
        # Clue scrolls
        if any(word in all_text for word in ['clue', 'treasure', 'hidey-hole', 'emote clue']):
            tags.append('Clue Scroll')
        
        # Minigames
        if any(word in all_text for word in ['minigame', 'castle wars', 'temple trek', 'pyramid plunder', 'dominion tower', 'tears of guthix', 'shattered worlds']):
            tags.append('Minigame')
        
        # Leveling tasks
        if any(word in all_text for word in ['level', 'reach level', 'total level', 'combat level']):
            tags.append('Leveling')
        
        # Food-related (eating tasks)
        if any(word in all_text for word in ['eat a', 'drink a']):
            tags.append('Food')
        
        # Remove duplicates and return
        return list(set(tags))
    
    def find_tasks_table(self, soup):
        """
        Locate the main tasks table in the HTML.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            BeautifulSoup element: Table element or None if not found
        """
        # Look for table with the specific header structure
        tables = soup.find_all('table')
        
        for table in tables:
            # Check if this table has the expected headers
            header_row = table.find('tr')
            if header_row:
                headers = header_row.find_all(['th', 'td'])
                header_texts = [self.clean_text(h).lower() for h in headers]
                
                # Look for our expected columns - must have all key headers
                expected_headers = ['area', 'task', 'information', 'requirements', 'pts']
                matching_headers = sum(1 for expected in expected_headers if expected in ' '.join(header_texts))
                
                # Ensure we have most of the expected headers and enough columns
                if matching_headers >= 4 and len(headers) >= 5:
                    # Additional check: make sure it's not a summary table
                    # Summary tables typically have very few rows
                    data_rows = table.find_all('tr')[1:]  # Skip header
                    if len(data_rows) > 20:  # Real task table should have many rows
                        logger.info(f"Found tasks table with {len(data_rows)} rows")
                        return table
                    else:
                        logger.debug(f"Skipping table with only {len(data_rows)} rows (likely summary)")
        
        # Fallback: look for table with sortable class that has many rows
        sortable_tables = soup.find_all('table', class_=lambda x: x and 'sortable' in x)
        for table in sortable_tables:
            data_rows = table.find_all('tr')[1:]  # Skip header
            if len(data_rows) > 20:
                logger.info(f"Found sortable table with {len(data_rows)} rows")
                return table
            
        logger.warning("Could not find tasks table")
        return None
    
    def scrape_tasks(self):
        """
        Main scraping method to extract all task data.
        
        Returns:
            list: List of dictionaries containing task data
        """
        # Fetch the webpage
        response = self.fetch_page()
        
        # Parse HTML
        logger.info("Parsing HTML...")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the tasks table
        table = self.find_tasks_table(soup)
        if not table:
            raise ValueError("Could not locate the tasks table on the page")
        
        # Find all data rows (skip header)
        rows = table.find_all('tr')[1:]  # Skip first row (header)
        logger.info(f"Found {len(rows)} data rows")
        
        tasks_data = []
        
        for i, row in enumerate(rows):
            try:
                cells = row.find_all(['td', 'th'])
                
                # Skip rows that don't have enough cells
                if len(cells) < 5:
                    logger.warning(f"Row {i+1} has insufficient cells ({len(cells)}), skipping")
                    continue
                
                # Extract data from each column
                area = self.extract_area_name(cells[0])
                task = self.clean_text(cells[1])
                information = self.clean_text(cells[2])
                requirements = self.process_requirements(cells[3])
                pts = self.extract_points(cells[4])
                
                # Generate tags based on task content
                tags = self.generate_tags(task, information, requirements, area, pts)
                
                task_data = {
                    'Area': area,
                    'Task': task,
                    'Information': information,
                    'Requirements': requirements,
                    'Pts': pts,
                    'Tags': tags
                }
                
                tasks_data.append(task_data)
                logger.debug(f"Processed row {i+1}: {area} - {task[:50]}...")
                
            except Exception as e:
                logger.error(f"Error processing row {i+1}: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(tasks_data)} tasks")
        return tasks_data
    
    def export_to_json(self, data, filename='catalyst_league_tasks.json'):
        """
        Export data to JSON file.
        
        Args:
            data (list): List of task dictionaries
            filename (str): Output filename
        """
        if not data:
            logger.warning("No data to export")
            return
        
        logger.info(f"Exporting {len(data)} tasks to {filename}...")
        
        # Convert data to proper format for JSON
        json_data = {
            "tasks": data,
            "metadata": {
                "total_tasks": len(data),
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "source_url": self.url
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully exported data to {filename}")
    
    def export_to_csv(self, data, filename='catalyst_league_tasks.csv'):
        """
        Export data to CSV file (fallback/legacy method).
        
        Args:
            data (list): List of task dictionaries
            filename (str): Output filename
        """
        if not data:
            logger.warning("No data to export")
            return
        
        logger.info(f"Exporting {len(data)} tasks to {filename}...")
        
        if HAS_PANDAS and pd is not None:
            # Use pandas for better CSV handling
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8')
        else:
            # Use csv module
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Area', 'Task', 'Information', 'Requirements', 'Pts', 'Tags']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(data)
        
        logger.info(f"Successfully exported data to {filename}")
    
    def run(self, export_format='json'):
        """
        Main execution method.
        
        Args:
            export_format (str): Format to export data ('json' or 'csv')
        """
        try:
            logger.info("Starting Catalyst League tasks scraper...")
            
            # Scrape the data
            tasks_data = self.scrape_tasks()
            
            # Export to specified format
            if export_format.lower() == 'json':
                self.export_to_json(tasks_data)
            else:
                self.export_to_csv(tasks_data)
            
            logger.info("Scraping completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return False

def main():
    """Main entry point."""
    import sys
    
    # Allow specifying format via command line argument
    export_format = 'json'
    if len(sys.argv) > 1:
        export_format = sys.argv[1].lower()
        if export_format not in ['json', 'csv']:
            print("Usage: python catalyst_league_scraper.py [json|csv]")
            return 1
    
    scraper = CatalystLeagueScraper()
    success = scraper.run(export_format)
    
    if success:
        print("\n✅ Scraping completed successfully!")
        if export_format == 'json':
            print("📄 Output file: catalyst_league_tasks.json")
        else:
            print("📄 Output file: catalyst_league_tasks.csv")
    else:
        print("\n❌ Scraping failed. Check the logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
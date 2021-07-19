import time
from OOP.WikimapiaChromeCrawler import WikimapiaChromeCrawler
from datetime import datetime

if __name__ == '__main__':
    now = datetime.now()
    timestamp = date_time = now.strftime("%m_%d_%Y")
    new_crawler = WikimapiaChromeCrawler()
    new_crawler.get_country_data_GeoJSON_bs4(country_name='Israel', output_file_name=f'result_{timestamp}')


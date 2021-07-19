import json
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
from .utils import country_cap

# import wikimapia_consts

CHROME_DRIVER = 'C:/Users/marmi/PycharmProjects/wikimapia/assets/drivers/chromedriver.exe'
WIKIMAPIA_MAIN_PAGE = 'https://wikimapia.org/'
COUNTRY_PAGE = 'https://wikimapia.org/country/'


class WikimapiaChromeCrawler:
    def __init__(self, driver_path=CHROME_DRIVER,
                 base_url=WIKIMAPIA_MAIN_PAGE):
        self.driver_path = driver_path
        # self.driver = webdriver.Chrome(self.driver_path)
        self.base_url = base_url
        self.countries_names = self.get_wiki_country_list()

    def get_wiki_country_list(self):
        """
        Gets dynamically countries list that available in wikimapia using bs4
        The countries list will be will used later to check if the client
        :return: List of countries list in wikimapia
        """
        print('Collecting current countries list in wikimapia')
        path_url = COUNTRY_PAGE
        page = requests.get(path_url)

        soup = BeautifulSoup(page.content, "html.parser")
        links = soup.find_all("ol", class_="linkslist")
        anchors = [link.findAll('a') for link in links]
        countries_name = []
        for link in anchors:
            for country in link:
                countries_name.append(country.text)
        print('Finished collecting current countries list in wikimapia')
        return countries_name

    def get_lat_long_z(self, map_link):
        """

        :param map_link:
        :return:
        """
        atr = ['longitude', 'latitude', 'zoom']
        if '=' in map_link:
            result_places = dict()
            split_str = map_link.split('=')
            for i in range(1, len(split_str)):
                result_places[atr[i - 1]] = split_str[i][:4]
            return result_places
        return None

    def get_country_data_GeoJSON_bs4(self, country_name, output_file_name='result'):
        """
        Getting country data in GeoJSON format
        :param country_name: country name, will be capitalized to check if he is the country list
        :param output_file_name: output file name
        :return:
        """
        country_name = country_cap(country_name)
        if country_name not in self.countries_names:
            raise ValueError('Country is not found in wikimapaia!')
        print(f'Started scanning {country_name}')
        country_name_link = country_name.replace(' ', '_')
        path_url = COUNTRY_PAGE + country_name_link + '/'
        page = requests.get(path_url)

        soup = BeautifulSoup(page.content, "html.parser")
        links_to_scan = []
        links = soup.find_all("div", class_="row-fluid")
        anchors = links[0].findAll('a', href=True)
        for link in anchors:
            curr_url = COUNTRY_PAGE + country_name_link + '/' + link['href']
            page = requests.get(curr_url)
            soup = BeautifulSoup(page.content, "html.parser")
            links = soup.find_all("div", class_="row-fluid")
            anchors = links[0].findAll('a', href=True)
            for i in range(0, len(anchors), 2):
                page = requests.get(curr_url + anchors[i]['href'])
                soup = BeautifulSoup(page.content, "html.parser")
                links_p = soup.find_all("div", class_="row-fluid")
                anchors_p = links_p[1].findAll('a', href=True)
                links_to_scan.append(anchors_p)
            print(COUNTRY_PAGE + country_name + '/' + link['href'])
            time.sleep(3)
        result = dict()
        for link_place in links_to_scan:
            # Runs on places link, not on map link - runs on list with jumps of 2
            for i in range(0, len(link_place), 2):
                print(link_place[i]['href'])
                curr_place = dict()
                page = requests.get(link_place[i]['href'])
                soup = BeautifulSoup(page.content, "html.parser")
                try:
                    content = soup.find_all('div', class_='row-fluid')[1]
                    title = content.find('h1').text.strip()
                    if len(content.find_all('div', {'id': 'place-description'})) > 0:
                        description = content.find_all('div', {'id': 'place-description'})[0].text.strip()
                    else:
                        description = None
                    try:
                        wiki_link = content.find('div', {'class': 'placeinfo-row wikipedia-link'}).a['href']
                    except:
                        print('No wiki link')
                        wiki_link = None
                    try:
                        category = content.find('div', {'id': 'placeinfo-categories'}).text.strip().split('\n')[0]
                    except:
                        print('No category')
                        category = None
                    cord = self.get_lat_long_z(link_place[i + 1]['href'])
                    curr_place['type'] = category
                    curr_place['title'] = title
                    curr_place['desc'] = dict()
                    curr_place['desc']['geo'] = cord
                    curr_place['desc']['wiki_link'] = wiki_link
                    curr_place['desc']['desc'] = description
                    result[i / 2] = curr_place
                except:
                    print(f"can't find {link_place[i]['href']}")
            time.sleep(3)

        with open(output_file_name + '.json', 'w') as json_file:
            json.dump(result, json_file)

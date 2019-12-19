from random import choice
import json
import pandas as pd
import re
from lxml.html import fromstring
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class Instaforce:

    def __init__(self, user_agents=None, proxy=None):
        self.user_agents = user_agents
        self.proxy = proxy
        self.proxies = self.__get_proxies()
        self.num = 1

    def __get_proxies(self):
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = set()
        for i in parser.xpath('//tbody/tr')[:10]:
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies.add(proxy)
        return proxies

    def __request_url(self, url):
        Proxy_pool = self.proxies
        i = len(Proxy_pool)
        try:
            response = requests.get(url)
            response.raise_for_status()
        except:
            index = 0
            for proxi in Proxy_pool:
                try :
                    response = requests.get(url,proxies={"http": proxi, "https": proxi})
                    print(response.json())
                except :
                    if index == i:
                        self.proxies = self.__get_proxies()
                        Proxy_pool = self.proxies
                        i = len(Proxy_pool)
                        index = 0
                    else :
                        print("Essaie connexion ip en cours")
                index += 1
        else:
            return response.text

    @staticmethod    
    def create_csvfile(self, df, content):
        df.to_csv(str(self.num) + '_' + content, index=False)
        self.num += 1

    @staticmethod
    def extract_json_data(html):
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('body')
        script_tag = body.find('script')
        raw_string = script_tag.text.strip().replace('window._sharedData =', '').replace(';', '')
        return json.loads(raw_string)
    
    def get_date_post(self, profile_url):
        results = []
        response = requests.get(profile_url)
        json_data = self.extract_json_data(response.text)
        metrics = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']["edges"]
        for node in metrics:
            node = node['node']['taken_at_timestamp']
            node = datetime.fromtimestamp(node)
            results.append(node)
        return results

    def get_htags(self, profile_url):
        results = []
        htags = []
        response = self.__request_url(profile_url)
        json_data = self.extract_json_data(response)
        metrics = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']["edges"]
        for node in metrics:
            if len(node['node']['edge_media_to_caption']['edges']):
                node = node['node']['edge_media_to_caption']['edges'][0]['node']['text']
                node = re.split(' |_|-|!', node)
                for htag in node:
                    i = htag.find('#')
                    if i != -1:
                        htags.append(htag[i:])
                results.append(htags)
            else :
                results.append(None)
            htags = []
        return results

    def get_img_url(self, profile_url):
        results = []
        response = self.__request_url(profile_url)
        json_data = self.extract_json_data(response)
        metrics = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']["edges"]
        for node in metrics:
            node = node['node']
            results.append(node['display_url'])
        return results
    
    def get_profile_info(self, profile_url):
        reponse = self.__request_url(profile_url)
        soup = BeautifulSoup(reponse, 'html.parser')
        data = soup.find_all('meta', attrs={'property': 'og:description'})
        return(data) 

    def get_nb_post(self, profile_url):
        post = self.get_profile_info(profile_url)
        for content in post:
            content = str(content)
            if content is not None:
                content = re.split(', |_|-|!', content)
                return(content[2])

    def get_post_info(self, profile_url):
        data = {}
        data['profile_url'] = profile_url
        data['img_url'] = self.get_img_url(profile_url)
        data['htag'] = self.get_htags(profile_url)
        data['date'] = self.get_date_post(profile_url)
        data_f = pd.DataFrame(data)
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            self.create_csvfile(self, data_f, "post_info.csv")
    
    def frequence(self, profile_url):
        moy = 0
        i = 0
        mois = {'01':0, '02':0, '03':0, '04':0, '05':0, '06':0, '07':0, '08':0, '09':0, '10':0, '11':0, '12':0}
        dates = self.get_date_post(profile_url)
        for date in dates:
            date = str(date)
            date = re.split(', |_|-|!', date)
            mois[date[1]] += 1
        for index in mois:
            if mois[index]:
                moy += mois[index]
                i += 1
        print(str(moy / i) + "/mois")
            

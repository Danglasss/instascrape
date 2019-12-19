from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.request import urlopen
import time
import re
import json

def connexion(url, browser):
    browser.get(url)
    source = browser.page_source
    data = BeautifulSoup(source, 'html.parser')
    return data

def get_htag(soup):
    links = []
    a = soup.findAll('a', attrs={'class': ''})
    for link in a:
        text = link.text
        if text.find('#') != -1:
            links.append(link.text)
    return links

def get_post_info(urls):
    browser = webdriver.Chrome()
    post_details = []
    i = 0
    for link in urls:
        soup = connexion(link, browser)
        jaime = soup.find_all('meta', attrs={'name': 'description'})
        time = soup.find("time")
        date = time.get('datetime')
        htags = get_htag(soup)
        i += 1
        if i == 1:
            break
        post_details.append({'jaime': jaime, 'date': date, 'htags' : htags})        
    #print(post_details)

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
from post_info import *

def get_info(url):
    browser = webdriver.Chrome()
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find_all('meta', attrs={'property': 'og:description'})
    print(data)

def connexion(url):
    browser = webdriver.Chrome()
    browser.get(url)
    source = browser.page_source
    data = BeautifulSoup(source, 'html.parser')
    return data

def get_link_post(url):
    links=[]
    data = connexion(url)
    body = data.find('body')
    a = body.findAll('a')
    for link in a:
        if re.match("/p", link.get('href')):
            links.append('https://www.instagram.com'+link.get('href'))
    get_post_info(links)


get_link_post("https://www.instagram.com/koffibearspirit/")


import config
import os.path
import re
import requests
import sys
import time
from os import path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

def findFiles():
    url = "https://www.thescore.org/"
    chrome_options = Options()
    chrome_options.headless = True
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    wait = WebDriverWait(driver, 30).until(presence_of_element_located((By.CLASS_NAME, "mejs-mediaelement")))
    downloadFiles(driver)

def downloadFiles(driver):
    articles = driver.find_elements_by_class_name("format-audio")
    for article in articles:
        audio = article.find_elements_by_css_selector("audio")
        if len(audio) > 0:
            title = extractTitle(article)
            # There should only be one audio file in each article
            url = extractUrl(audio[0])
            download(url, title)

def extractTitle(article):
    titleWrapper = article.find_element_by_class_name("entry-title")
    titleLink = titleWrapper.find_element_by_tag_name('a')
    return titleLink.get_attribute('innerText')

def extractUrl(audio):
   source = audio.find_element_by_css_selector('source')
   return source.get_attribute('src')

def download(url, title):
    datePieces = extractDate(url)
    localFile = path.join(config.download_dir, formatName(datePieces, title))
    if not path.exists(localFile):
        if config.dry_run:
            print("Downloading %s\n" % url)
        else:
            remote = requests.get(url, allow_redirects=True)
            open(localFile, 'wb').write(remote.content)

def extractDate(url):
    fileRegex = re.compile(r'https://daisy.allclassical.org/ondemand/([\d]+)-([\d]+)-([\d]+).*')
    return re.findall(fileRegex, url)[0]

def formatName(datePiece, title):
    return "%s-%s-%s-%s.mp3" % (datePiece[0], datePiece[1], datePiece[2], pascalCase(title))

def pascalCase(s):
    return ''.join(i for i in s.title() if not i.isspace())

findFiles()



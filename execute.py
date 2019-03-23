#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""

@author: zaraki673
@author: k20human
source: tangix

"""

#
# Copyright (C) 2019 Kévin Mathieu
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.
#

from selenium import webdriver
import http.cookiejar
import urllib
import json
import os
import sys
import time
import base64
import csv
import logging
from logging.handlers import RotatingFileHandler

configurationFile = './config.json'

# Configure logs
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

file_handler = RotatingFileHandler('veolia.log', 'a', 1000000, 1)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

steam_handler = logging.StreamHandler()
steam_handler.setLevel(logging.INFO)
steam_handler.setFormatter(formatter)
logger.addHandler(steam_handler)

# Check if configuration file exists
if os.path.isfile(configurationFile):
    # Import configuration file
    with open(configurationFile) as data_file:
        config = json.load(data_file)
else:
    logger.error('Your configuration file doesn\'t exists')
    sys.exit('Your configuration file doesn\'t exists')

# domoticz server & port information
domoticzserver = config['domoticz_server']

# domoticz IDX
domoticzIdx = config['domoticz_idx']

# domoticz user
domoticzlogin = config['domoticz_login']

# domoticz password
domoticzpassword = config['domoticz_password']

# Veolia Login
Vlogin = config['login']

# Veolia password
Vpassword = config['password']

downloadPath = '/tmp'
downloadFile = downloadPath + '/historique_jours_litres.csv'

class URL:
    def __init__(self):
        # On active le support des cookies pour urllib
        cj = http.cookiejar.CookieJar()
        self.urlOpener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    def call(self, url, params=None, referer=None, output=None):
        logger.info('Calling url: %s', url)
        data = None if params == None else urllib.parse.urlencode(params).encode("utf-8")
        request = urllib.request.Request(url, data)

        if referer is not None:
            request.add_header('Referer', referer)

        response = self.urlOpener.open(request)
        logger.info(" -> %s" % response.getcode())
        if output is not None:
            file = open(output, 'w')
            file.write(response.read())
            file.close()
        return response


argsweb = 'ok'
# WebSite gathering
if argsweb:
    url = URL()

    urlHome = 'https://espace-client.vedif.eau.veolia.fr/s/login/'
    urlConso = 'https://espace-client.vedif.eau.veolia.fr/s/historique'

    profile = webdriver.FirefoxProfile()
    options = webdriver.FirefoxOptions()
    options.headless = True
    profile.set_preference('browser.download.folderList', 2)  # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', downloadPath)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

    browser = webdriver.Firefox(firefox_profile=profile, firefox_options=options)

    browser.implicitly_wait(10)

    # Connect to Veolia website
    logger.info('Connexion au site Veolia Eau Ile de France')

    browser.get(urlHome)

    # Fill login form
    idEmail = browser.find_element_by_id("input-4")
    idPassword = browser.find_element_by_css_selector("input[type='password']")

    idEmail.send_keys(Vlogin)
    idPassword.send_keys(Vpassword)

    loginButton = browser.find_element_by_class_name('submit-button')
    loginButton.click()

    time.sleep(5)

    # Page 'votre consomation'
    logger.info('Page de consommation')
    browser.get(urlConso)
    time.sleep(5)

    # Download file
    logger.info('Telechargement du fichier')
    downloadFileButton = browser.find_element_by_class_name("slds-button")
    downloadFileButton.click()

    browser.close()

    with open(downloadFile, 'r') as f:
        for row in reversed(list(csv.reader(f, delimiter=';'))):
            volume = int(row[1])
            logger.info('Volume: %s', str(volume))

            if domoticzlogin:
                b64domoticzlogin = base64.b64encode(domoticzlogin.encode())
                b64domoticzpassword = base64.b64encode(domoticzpassword.encode())
                urldom = 'http://' + domoticzserver + '/json.htm?username=' + b64domoticzlogin.decode()  + '&password=' + b64domoticzpassword.decode() + '&type=command&param=udevice&idx=' + domoticzIdx + '&svalue=' + str(
                    volume) + ''
            else:
                urldom = 'http://' + domoticzserver + '/json.htm?type=command&param=udevice&idx=' + domoticzIdx + '&svalue=' + str(
                    volume) + ''
            url.call(urldom)

    # Remove file
    os.remove(downloadFile)

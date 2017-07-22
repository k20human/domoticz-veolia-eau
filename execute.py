#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""

@author: zaraki673
@author: k20human
source: tangix

"""

import http.cookiejar, urllib
import xlrd
from xlrd.sheet import ctype_text

# domoticz server & port information
domoticzserver = "192.168.10.28:8080"

# domoticz IDX
Idx = "domoticz_idx"

# Veolia Login
Vlogin = ""

# Veolia password
Vpassword = "your_password"


# Logger
def Logger(pMessage):
    file = open('veoliaconnect.log', 'a')
    file.write("%s\n" % pMessage)
    file.close()


class URL:
    def __init__(self):
        # On active le support des cookies pour urllib
        cj = http.cookiejar.CookieJar()
        self.urlOpener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    def call(self, url, params=None, referer=None, output=None):
        Logger('Calling url')
        data = None if params == None else urllib.parse.urlencode(params).encode("utf-8")
        request = urllib.request.Request(url, data)
        if referer is not None:
            request.add_header('Referer', referer)
        response = self.urlOpener.open(request)
        Logger(" -> %s" % response.getcode())
        if output is not None:
            file = open(output, 'w')
            file.write(response.read())
            file.close()
        return response


argsweb = 'ok'
# WebSite gathering
if argsweb:
    url = URL()

    urlConnect = 'https://www.service-client.veoliaeau.fr/home.loginAction.do#inside-space'
    urlConso1 = 'https://www.service-client.veoliaeau.fr/home/espace-client/votre-consommation.html'
    urlConso2 = 'https://www.service-client.veoliaeau.fr/home/espace-client/votre-consommation.html?vueConso=historique'
    urlXls = 'https://www.service-client.veoliaeau.fr/home/espace-client/votre-consommation.exportConsommationData.do?vueConso=historique'
    urlDisconnect = 'https://www.service-client.veoliaeau.fr/logout'

    # Connect to Veolia website
    Logger('Connection au site Veolia Eau')
    params = {'veolia_username': Vlogin,
              'veolia_password': Vpassword,
              'login': 'OK'}
    referer = 'https://www.service-client.veoliaeau.fr/home.html'
    url.call(urlConnect, params, referer)

    # Page 'votre consomation'
    Logger('Page de consommation')
    url.call(urlConso1)

    # Page 'votre consomation : historique'
    Logger('Page de consommation : historique')
    url.call(urlConso2)

    # Download XLS file
    Logger('Telechargement du fichier')
    response = url.call(urlXls)
    content = response.read()

    # logout
    Logger('Deconnection du site Veolia Eau')
    url.call(urlDisconnect)

    file = open('temp.xls', 'wb')
    file.write(content)
    file.close()

    book = xlrd.open_workbook('temp.xls', encoding_override="cp1252")
    sheet = book.sheet_by_index(0)
    last_rows = sheet.nrows
    row = sheet.row(last_rows - 1)
    for idx, cell_obj in enumerate(row):
        cell_type_str = ctype_text.get(cell_obj.ctype, 'unknown type')
        if idx == 1:
            volume = int(cell_obj.value)
            urldom = 'http://' + domoticzserver + '/json.htm?type=command&param=udevice&idx=' + Idx + '&svalue=' + str(
                volume) + ''
            url.call(urldom)

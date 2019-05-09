import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import sqlite3
from django.db.models import Min, Q, Count, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractYear
import time
from requests import get
from random import randint
import sys
# pip install PyQt5 and PyQtWebEngine
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QUrl
#from PyQt5.QtWebEngineWidgets import QWebPage
#from PyQt5.QtWebEngine import QtWebEngine as QWebPage

from PyQt5.QtWebEngineWidgets import QWebEngineView
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from selenium import webdriver
#

# class Client(QWebEngineView):
#
#     def __init__(self, url):
#         self.app = QApplication(sys.argv)
#         QWebEngineView.__init__(self)
#         self.loadFinished.connect(self.on_page_load)
#         self.mainFrame().load(QUrl(url))
#         #print (url)
#         #self.load(QUrl(url))
#         self.app.exec_()
#
#     #def on_page_load(self):
#     #    self.app.quit()
#
# #  def _loadFinished(self, result):
# #      self.page().toHtml(self._callable)
# #
# #  def _callable(self, data):
# #      self.html = data
# #      self.app.quit()
# #
# # return render(source_url).html
#
# # url = "https://etfdb.com/etf/SPY/#etf-holdings&sort_name=weight&sort_order=desc&page=8"
# url = "https://www.etf.com/SPY#fit"
# # #print (render(url))
# client_response = Client(url)
# source = Render(url)
# source = client_response.mainFrame().toHtml()
# soup = BeautifulSoup(source, 'lxml')
# print (soup.text)
# for symbol in soup.find("div", {'class':'view_all_table'}):
#
#      if isinstance(symbol.find('td'), int):
#          continue
#      else:
#          product = symbol.find_all('td')
#          ticker = product[0].text
#          weight = product[1].text
#          print (ticker, weight)
# #
#
#

def get_schedule():

    from bs4 import BeautifulSoup
    import urllib.request
    #page = 1
    #base_url = "https://etfdb.com/etf/SPY/#etf-holdings&sort_name=weight&sort_order=desc&page="

    #print (base_url + str(page))
    #total_prods = 506

    #while total_prods > page * 15:
    #html = urllib.request.urlopen(str(base_url) + str(page))
    browser = webdriver.Chrome()
    html = browser.get("https://www.etf.com/SPY")
    print ('html', html)
    soup = BeautifulSoup(html, 'html.parser')

    #for symbol in soup.find_all("tbody")[2]:
    symbols = soup.find("div", {'class':'view_all_table'})
    table = symbols.find('tbody')
    print ('---------starting for--------')
    print (len(table), type(table), table)
    for row in table:
        print ('row', row.find('td'))
        for data in row:
            print (type(data))
            if isinstance(data.find('td'), int):
                print ('int')
            else:
                product = data.find_all('td')
                ticker = product[0].text
                weight = product[1].text
                print (ticker, weight)
            #for td in symbol.find_all('td'):
            #    print (td)
    #page += 1

        print ('-------start session test-------')
        # session = HTMLSession()
        #
        # r = session.get('https://etfdb.com/etf/SPY/#etf-holdings&sort_name=weight&sort_order=desc&page=8')
        # r.html.render()
        # test = r.html.search('Boston')
        # print (test)
        import dryscrape
        sess = dryscrape.Session()
        sess.visit("https://etfdb.com/etf/SPY/#etf-holdings&sort_name=weight&sort_order=desc&page=8")
        page = sess.body()

        soup = BeautifulSoup(page, 'html.parser')

        for symbol in soup.find_all("tbody")[2]:
            if isinstance(symbol.find('td'), int):
                continue
            else:
                product = symbol.find_all('td')
                ticker = product[0].text
                weight = product[1].text
                print (ticker, weight)


#get_schedule()

def check_scores():
    t = Tournament.objects.get(current=True)
    userL = ['john', 'jcarl62', 'BigDipper', 'Laroqm', 'ryosuke', 'shishmeister', 'JoeLong']
    for u in userL:
        print (u, ScoreDetails.objects.filter(user=User.objects.get(username=u), pick__playerName__tournament=t).values('user').aggregate(Count('user')))



check_scores()

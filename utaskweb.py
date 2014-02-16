#!/usr/bin/env python3
#-*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import requests
import sys
root = "https://zkyomu.c.u-tokyo.ac.jp"

class utaskweb:
    """ This is a class of crawling utaskweb """
    def __init__(self):
        self.session = requests.session()

    def meta_refresh(self):
        soup  = BeautifulSoup(self.response.text)
        result = None
        for meta in soup.find_all("meta"):
            if meta.attrs['http-equiv'].lower() == "refresh":
                result = meta
        if result:
            url = result["content"].split(";")[1].strip()
            self.response = self.session.get(root + url[4:])
            return True
        return None

    def login_utaskweb(self, username, password, code_number):
        print("Logging in UTask-Web...")
        url = root + "/utask/campus"
        data = {'view': 'view.initial',
                'func': 'function.login',
                'usernm': username,
                'passwd': password,
                'code_num': code_number,}
        headers = {'User-Agent': 'Mozilla/5.0(Windows;U;Windows NT 5.1;rv:1.7.3) Gecko/20041001Firefox/0.10.1'}
        self.response = self.session.post(url, data=data, headers=headers)
        if not self.meta_refresh():
            return None

    def syllabus_link(self):
        """ Get syllabus refering link"""
        print("Crawling syllabus in Utask-Web...")

        # find frame tag which contains syllabus link
        menu = None
        for frame in BeautifulSoup(self.response.text).find_all('frame'):
            if frame.attrs['name'] == "menu":
                self.response = self.session.get(root+frame.attrs['src'])
        soup = BeautifulSoup(self.response.text)
        menu_open = None
        for k, v in enumerate(soup.find_all('a')):
            if k is 9:
                menu_open = v.attrs['href']
        if menu_open is None:
            print('Login failed or have some problem, please try again.')
            sys.exit()
        else:
            url = root + menu_open
        self.response = self.session.get(url)
        soup = BeautifulSoup(self.response.text)
        syllabus_link = None
        for k, v in enumerate(soup.find_all('a')):
            if k is 10:
                syllabus_link = v.attrs['href']
        url = root + syllabus_link
        self.response = self.session.get(url)
        if not self.response:
            return None

    def search_syllabus(self, nendo=2013, semester=""):
        print("Starting search in syllabus...")
        soup = BeautifulSoup(self.response.text)
        ott4cs = soup.find('input', attrs={'name':'ott4cs'}).attrs['value']
        url = root + soup.find('form', attrs={'name': 'SearchForm'}).attrs['action']
        gakki = None
        if semester is "summer":
            gakki = 1
        elif semester is "winter":
            gakki = 2
        data = {'view': 'view.syllabus.refer.search.input.gakusei',
                'ott4cs': ott4cs,
                'func': 'function.syllabus.refer.search',
                's_type': '1',
                'nendo': nendo,
                'j_s_cd': '0A',
                'gakki': gakki,
                'kamoku_kbn': '',
                'keyword': '',
                'kamokunm': '',
                'kyokannm_kanji': '',
                'kyokannm_kana': '',
                'k_s_cd': '',
                'nenji': '',
                'yobi': '',
                'jigen': '',
                'disp_cnt': '200',}
        headers = {'User-Agent': 'Mozilla/5.0(Windows;U;Windows NT 5.1;rv:1.7.3) Gecko/20041001Firefox/0.10.1'}
        self.response = self.session.post(url, data=data, headers=headers)
        return self.response

    ## Crawl the result of search
    def search_results(self):
        print("Crawling the results of search...")
        soup = BeautifulSoup(self.response.text)
        crawled = []
        results = []
        while(True):
            pages = []
            for a in soup.find_all('a'):
                if a.attrs['href'].find('s_no') != -1:
                    pages.append(root + a.attrs['href'])
                elif a.attrs['href'].startswith('/utask/campus?view=view.syllabus.refer.search'):
                    results.append(root + a.attrs['href'])
            url = pages[-1]
            self.response = self.session.get(url)
            soup = BeautifulSoup(self.response.text)
            if url.split('s_no=')[1] in crawled:
                break
            else:
                crawled.append(url.split('s_no=')[1])
        return results

    def scrape_syllabus(self, url):
        response = self.session.get(url)
        soup = BeautifulSoup(response.text)
        titles = []
        contents = []
        for th in soup.find_all('th', attrs={'class': 'syllabus-normal'}):
            if th:
                titles.append(th.get_text(strip=True))

            idx = th.parent.find_all('th').index(th) # scraping table index
            if th.next_sibling.next_sibling == None:
                continue
            elif th.next_sibling.next_sibling.name == 'th':
                contents.append(th.parent.next_sibling.next_sibling.find_all('td')[idx].get_text(strip=True))
            else:
                contents.append(th.next_sibling.next_sibling.get_text(strip=True))
        return dict(zip(titles, contents))

#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/../')
from utaskweb import utaskweb
import getpass
import csv

def all_syllabus():
    print("Starting Crawling https://zkyomu.c.u-tokyo.ac.jp...")
    username = input("ID:")
    password = getpass.getpass("パスワード:")
    code_number = getpass.getpass("暗証番号:")

    utask = utaskweb()
    res = utask.login_utaskweb(username=username,
                               password=password,
                               code_number=code_number)
    utask.syllabus_link()
    utask.search_syllabus(nendo=2013, semester="winter")
    results = utask.search_results()

    data = []
    print("Scraping the syllabus...")
    for result in results:
        data.append(utask.scrape_syllabus(url=result))

    filename = "out.csv"
    with open(filename, 'w', encoding="utf-16") as f:
        for d in data:
            w = csv.DictWriter(f, d.keys())
            if data.index(d) == 0:
                w.writeheader()
            w.writerow(d)
    f.close()


if __name__ == "__main__":
    all_syllabus()

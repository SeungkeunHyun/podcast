#!c:\ProgramData\Anaconda3\python
import re
import json
from lxml import html
import requests
import cgi
import urllib.request
import ast
import datetime
from lxml import html
import sys


def parsePage(purl, episodes):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    req = urllib.request.Request(purl, None, headers)
    with urllib.request.urlopen(req) as resp:
        respText = resp.read().decode('utf-8')
    jsonItems = re.findall(
        'episode\[\d+\] = ({[^}]+})', respText)
    page = html.fromstring(respText)
    for jsonItem in jsonItems:
        episode = {}
        jsonItem += ""
        jsonItem = jsonItem.strip().replace("'ischsell':ischsell", '"dummy": 1')
        # self.log(jsonItem)
        datItem = ast.literal_eval(jsonItem)
        episode['title'] = datItem['title']
        if datItem['pubdate'] == 'Today':
            episode['pubdate'] = datetime.today().strftime('%Y/%m/%d')
        else:
            episode['pubDate'] = datItem['pubdate'][:4] + '/' + \
                datItem['pubdate'][4:6] + '/' + datItem['pubdate'][6:8]
        episode['mediaURL'] = datItem['down_file']
        episode['duration'] = page.xpath('//li[@epiuid="' + datItem['player_down'].split(
            '=')[-1] + '"]/dl/dd[@class="dd_time"]/text()')[0].strip()
        episodes.append(episode)
    if "?page" not in purl:
        purl = purl + "?page=1"
    if len(page.xpath('//img[@alt="다음"]')) > 0:
        pg = re.findall("\?page=(\d+)", purl)[0]
        pg = int(pg) + 1
        if pg > 3:
            return
        purl = re.sub('page=\d+', 'page=%d' % pg, purl).strip()
        sys.stderr.write('current url is %s\n' % purl)
        parsePage(purl, episodes)


episodes = list()
print("Content-Type: application/json; charset: utf-8\n")
params = cgi.FieldStorage()
castid = params['castid'].value
requrl = "http://www.podbbang.com/ch/%s/" % castid
# print(respText)
parsePage(requrl, episodes)
print(json.dumps(episodes))

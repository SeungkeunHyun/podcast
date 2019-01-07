#!c:\ProgramData\Anaconda3\python
import re
import json
from lxml import html
import requests
import cgi
import urllib
import ast
import datetime
from lxml import html
import sys

params = cgi.FieldStorage()
term = params['term'].value
totalResult = {}
def search_itunes(term):
	suri = 'https://itunes.apple.com/search?term='
	qry = suri + term
	res = requests.get(qry).json()
	hits = list()
	if res['resultCount'] == 0:
		return hits
	for r in res['results']:
		hit = {}	
		hit['provider'] = 'itunes'
		for k, v in r.items():
			if k == 'feedUrl':
				hit['feedURL'] = v
			if k == 'trackName':
				hit['name'] = v
			if k == 'artworkUrl60':
				hit['imageURL'] = v
			if k == 'genres':
				hit['category'] = ','.join(v)
			if k == 'trackId':
				hit['podcastID'] = v
		hit['cast_episode'] = 'cast'
		hits.append(hit)
	return hits

def search_podbbang(term):
	suri = 'http://www.podbbang.com/category/lists?keyword=' + term
	res = requests.get(suri, headers={'User-Agent': 'Custom'})
	#print(res.text)
	page = html.fromstring(res.text)
	reslist = page.cssselect('#podcast_list div.inner')
	hits = list()
	for item in reslist:
		rec = {}
		rec['provider'] = 'podbbang'		
		rec['imageURL'] = item.cssselect('li img')[0].get('src')
		info = item.cssselect('li.section_2 dt a')[0];
		rec['name'] = info.text_content()
		rec['feedURL'] = 'http://www.podbbang.com' + info.get('href')
		rec['podcastID'] = rec['feedURL'].split('/')[-1]
		rec['category'] = item.cssselect('li.section_2 div.cate')[0].get('title')
		rec['cast_episode'] = 'cast'
		hits.append(rec)
	return hits

def search_podty(term):
	suri = 'https://www.podty.me/search/total?keyword=' + term
	res = requests.get(suri, headers={'User-Agent': 'Custom'})
	#print(res.text)
	page = html.fromstring(res.text)
	reslist = page.cssselect('#castResults li')
	res = list()
	for item in reslist:
		rec = {}
		info = item.cssselect('figure.castEpisodeInfo a')[0]
		img = info.cssselect('img')[0]
		rec['provider'] = 'podty'
		rec['imageURL'] = img.get('src').strip()
		rec['name'] = img.get('alt').strip()
		rec['feedURL'] = 'https://www.podty.me' + info.get('href')
		rec['podcastID'] = info.get('href').split('/')[-1]
		rec['cast_episode'] = 'cast'
		res.append(rec)
	return res
	
print("Content-Type: application/json; charset: utf-8\n")
#print("Access-Control-Allow-Origin: *\n")
itunes_res = search_itunes(term)
if len(itunes_res) > 0:
	totalResult['itunes'] = itunes_res

podbbang_res = search_podbbang(term)
if len(podbbang_res) > 0:
	totalResult['podbbang'] = podbbang_res

podty_res = search_podty(term)	
if len(podty_res) > 0:
	totalResult['podty'] = podty_res
print(json.dumps(totalResult))

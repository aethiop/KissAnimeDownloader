# -*- coding: utf-8 -*-
"""
A script to get the download-url of KissAnime.ru but for now it only works
with fetching the lowest possible quality. 
"""


#Importing the libraries
import cfscrape
from bs4 import BeautifulSoup as bsoup
import re
from flask import Flask, render_template,request
import requests

#The URL to be used for the stored links
BASE_URL = "https://kissanime.ru"
END_URL = "&s=rapidvideo"
app = Flask(__name__)

@app.route('/Anime/<anime>')
def get_kissanime_url(anime):
	#Url of the series to be downloaded
	download_urls = []
	download_names = []

	
	seriesurl = BASE_URL + "/Anime/" + anime
	print(seriesurl)
	name_series = anime.replace("-"," ")
	#Use cfscrape to scrape web because of the 
	try:
		scrape = cfscrape.create_scraper()
		content_html = scrape.get(seriesurl)
		print("{0} Successfully loaded".format(name_series))
	except ConnectionError:
		print("Error in connection, Retrying...")
		content_html = scrape.get(seriesurl)
	
	#Souping the the page
	souped = bsoup(content_html.content,'html.parser')
	
	#Listing all links to the episodes
	episodes= souped.select('.listing a[href]')
	#Reverse them in the right order
	episodes.reverse()
	num_episodes = len(episodes)
	print(str(num_episodes) + " episodes in total")
	
	#Itterate through all the links to scrape another page
	i = 0
	for episode in episodes:
		i += 1
		#The url to the episode 
		episodes_link = BASE_URL + episode.attrs['href'] + END_URL
		
		#Scrape the episode page
		try:
			episode_page = scrape.get(episodes_link).content
			print("Successfully loaded episode {0}".format(i))
		except:
			print("Error in connection, Retrying...")
			episode_page = scrape.get(episodes_link).content
		
		episode_souped = bsoup(episode_page,'lxml')
		next_url = re.findall(r'http[s]://www.rapidvid.to/[a-z]/\w{10}',episode_souped.text)
		print(next_url)
		#Replace the /e/ with /d/ to get the download links
		next_url[0] = next_url[0].replace("/e/","/d/")
		
		#Scarp the download page
		try:
			download_page = scrape.get(next_url[0]).content
			print("Successfully loaded the download page")
		except ConnectionError:
			print("Error in connection, Retrying...")
			download_page = scrape.get(next_url[0]).content
			
		download_souped = bsoup(download_page,'lxml')
		downloadlink = download_souped.select('p.title a')
		url = ""
		
		if len(downloadlink) >= 1:
			url = downloadlink[0].attrs['href'] 
		else:
			url = ""
		
		
		#Appending the download link to the list
		download_urls.append(url)
	for i in range(num_episodes):
		ep = "Episode {0}: ".format(i+1) + name_series
		download_names.append(ep)
		
	return render_template('index.html', len = len(download_urls),download_urls = download_urls, download_names = download_names )
@app.route('/', methods = ['GET'])
def search():
	search_urls = []
	result_name = []
	if request.args.get('q'):
		query = request.args.get("q")
		with cfscrape.create_scraper() as cf:
			response = cf.post("https://kissanime.ru/Search/Anime", data={'keyword' : query})
			soup = bsoup(response.text,'html.parser')
			search_results = soup.select('.listing a[href]')
		for r in search_results:
			if '?id=' not in str(r):
				search_urls.append(r.attrs['href'])
				result_name.append(r.text)
	
	return render_template('index.html', len = len(result_name),download_urls = search_urls,download_names = result_name)
    # An authorised request
    #r = s.get(get_url, verify=False)
    #print r.text


if __name__ == "__main__":
	app.run(debug=True)
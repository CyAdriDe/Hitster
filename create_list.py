import pandas as pd
import time
import csv
import qrcode
import requests
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def create_list():
	with open('tracks.csv', 'r') as f:
		musica = []
		reader = csv.reader(f, delimiter = ",")
		for row in reader:
			musica.append(row)
	musica = musica[::-1]
	musica.pop() # Eliminem el títol de la columna
	
	return musica

def create_qr(item):
    qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5)
    qr.add_data(item[3])
    qr.make(fit=True)
    titol = item[0].replace("/", "")
    img = qr.make_image(fill='black', back_color='white')
    img.save(f'tracks/{titol}_{item[1]}_{item[2]}.png')

def get_token():
	url = 'https://accounts.spotify.com/api/token'
	payload = {
	    'grant_type': 'client_credentials',
	    'client_id': os.getenv('CLIENT_ID'),
	    'client_secret': os.getenv('CLIENT_SECRET')
	}
	headers = {
	    'Content-Type': 'application/x-www-form-urlencoded'
	}
	response = requests.post(url, data=payload, headers=headers)

	return response.json()['access_token']

def get_playlist(token):
	playlist_id = os.getenv('PLAYLIST_ID')
	url = 'https://api.spotify.com/v1/playlists/'+playlist_id+'/tracks?fields=items%28track%28id%29%29'
	headers = {
	    'Authorization': 'Bearer ' + token
	}
	response = requests.get(url, headers=headers)
	tracks = response.json()['items']
	list_ids = []
	for i in tracks:
		list_ids.append(i['track']['id'])
	return list_ids

def get_info(token, list_ids):
	headers = {
	    'Authorization': 'Bearer ' + token
	}
	#Borrem l'arxiu anterior
	with open('songs.csv', 'w', newline='') as file:
			writer = csv.writer(file)
			fields = ['Titulo','Artista','Año','URL']
			writer.writerow(fields)
			file.close()
	for track_id in list_ids:
		url = 'https://api.spotify.com/v1/tracks/'+ track_id
		response = requests.get(url, headers=headers)
		response = response.json()
		print(response['external_urls']['spotify'])
		info = [response['name'], response['artists'][0]['name'], response['album']['release_date'][0:4], response['external_urls']['spotify']]
		create_qr(info)
		with open('songs.csv', 'a', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(info)
			file.close()


if __name__ == '__main__':
	load_dotenv()
	token = get_token()
	list_ids = get_playlist(token)
	get_info(token, list_ids)

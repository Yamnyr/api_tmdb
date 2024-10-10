import gzip
import requests
import time
import pandas as pd
from database import insert_into_db
from datetime import datetime, timedelta
import streamlit as st
import json
import os

API_KEY = 'c7cf1f564fa32aed665c2abb44d2ffb9'
BASE_URL = 'https://api.themoviedb.org/3'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'
DATA_DIR = 'data'

def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {'api_key': API_KEY, 'language': 'fr-FR'}

    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            movie_details = {
                'id': movie_id,
                'title': data.get('title'),
                'release_date': data.get('release_date'),
                'genres': [genre['name'] for genre in data.get('genres', [])],
                'popularity': data.get('popularity'),
                'vote_average': data.get('vote_average'),
                'poster_url': f"{IMAGE_BASE_URL}{data.get('poster_path')}" if data.get('poster_path') else "Pas de poster disponible",
                'overview': data.get('overview', 'Pas de synopsis disponible')  # Ajout du synopsis
            }
            return movie_details
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 5))
            st.warning(f"Trop de requêtes. Attente de {retry_after} secondes...")
            time.sleep(retry_after)
        elif response.status_code == 404:
            st.error(f"Erreur : Film avec ID {movie_id} non trouvé.")
            return None
        else:
            st.error(f"Erreur : Statut {response.status_code} lors de la requête.")
            return None

def download_and_extract_tmdb_ids():
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%m_%d_%Y')
    url = f"https://files.tmdb.org/p/exports/movie_ids_{yesterday}.json.gz"
    gz_file = os.path.join(DATA_DIR, f"movie_ids_{yesterday}.json.gz")  # Enregistrer dans le dossier data
    json_file = os.path.join(DATA_DIR, f"movie_ids_{yesterday}.json")  # Enregistrer dans le dossier data

    try:
        st.info(f"Téléchargement du fichier : {gz_file}")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(gz_file, 'wb') as f:
            f.write(response.content)
        st.success("Téléchargement terminé.")

        with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
            content = f.readlines()

        st.info(f"Fichier décompressé : {json_file}")

        with open(json_file, 'w', encoding='utf-8') as f:
            f.writelines(content)
        st.success(f"Fichier JSON enregistré : {json_file}")

        movie_ids = [json.loads(line)['id'] for line in content]
        st.success(f"{len(movie_ids)} IDs de films extraits.")

        movies_details = []
        max_movies_to_process = 100

        progress_bar = st.progress(0)
        status_text = st.empty()

        for index, movie_id in enumerate(movie_ids[:max_movies_to_process]):
            progress_bar.progress((index + 1) / max_movies_to_process)
            status_text.text(f"Traitement du film {index + 1}/{min(max_movies_to_process, len(movie_ids))} (ID: {movie_id})")

            details = get_movie_details(movie_id)
            if details:
                movies_details.append(details)

        df = pd.DataFrame(movies_details)
        insert_into_db(df)

        st.success(f"Traitement terminé pour {max_movies_to_process} films.")

    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors du téléchargement : {e}")
    except Exception as e:
        st.error(f"Erreur : {e}")
def list_popular_movies():
    url = f"{BASE_URL}/movie/popular"
    params = {'api_key': API_KEY, 'language': 'fr-FR', 'page': 1}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        movies = data.get('results', [])
        return movies
    else:
        st.error(f"Erreur : Statut {response.status_code} lors de la requête.")
        return []
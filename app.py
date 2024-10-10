import streamlit as st
from movie_api import get_movie_details, list_popular_movies, download_and_extract_tmdb_ids, get_last_upload_info
from datetime import datetime

st.set_page_config(layout="wide")

st.title("TP TMDB API")

menu = st.sidebar.selectbox("Choisissez une option :", ("Rechercher un film", "Télécharger les IDs de films", "Lister les films populaires"))

if menu == "Rechercher un film":
    movie_id = st.number_input("Veuillez entrer l'ID du film :", min_value=0)
    if st.button("Rechercher"):
        details = get_movie_details(movie_id)
        if details:
            card_html = f"""
            <div style="border: none; border-radius: 8px; padding: 10px; margin: 10px; display: flex; align-items: center; background-color: #262730; transition: transform 0.2s; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <img src="{details['poster_url']}" style="width: 25%; border-radius: 5px; margin-right: 10px;"/>
                <div style="flex: 1;">
                    <h5 style="margin: 5px 0;">{details['title']}</h5>
                    <p style="margin: 5px 0;"><strong>Date de sortie :</strong> {details['release_date']}</p>
                    <p style="margin: 5px 0;"><strong>Popularité :</strong> {details['popularity']}</p>
                    <p style="margin: 5px 0;"><strong>Note moyenne :</strong> {details['vote_average']}</p>
                    <h6 style="margin: 5px 0;">Synopsis :</h6>
                    <p>{details['overview']}</p>
                    <a href="https://embed.su/embed/movie/{movie_id}" target="_blank" style="text-decoration: none;">
                        <button style="padding: 2px 50px; font-size: 16px; background-color: #0e1117; color: white; border: none; border-radius: 5px; cursor: pointer;">
                            Voir
                        </button>
                    </a>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

elif menu == "Télécharger les IDs de films":
    last_upload_id, last_upload_date = get_last_upload_info()

    if last_upload_date:
        formatted_date = datetime.strptime(last_upload_date, "%d_%m_%Y").strftime("%d/%m/%Y")
        st.markdown(f"### Dernier upload : {formatted_date}")
    else:
        st.markdown("### Aucun téléchargement antérieur trouvé.")

    if st.button("Télécharger et extraire les IDs des films d'hier"):
        download_and_extract_tmdb_ids()

elif menu == "Lister les films populaires":
    movies = list_popular_movies()
    if movies:
        st.subheader("Films Populaires")

        cols = st.columns(4)

        for index, movie in enumerate(movies):
            with cols[index % 4]:
                card_html = f"""
                <div style="border: none; border-radius: 8px; padding: 10px; margin: 10px; text-align: center; background-color: #262730; transition: transform 0.2s; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <img src="https://image.tmdb.org/t/p/w500{movie['poster_path']}" style="width: 100%; border-radius: 5px;"/>
                    <h5 style="margin: 5px 0; color: white;">{movie['title']}</h5>
                    <p style="margin: 5px 0; color: white;"><strong>Date de sortie :</strong> {movie['release_date']}</p>
                    <p style="margin: 5px 0; color: white;"><strong>Popularité :</strong> {movie['popularity']}</p>
                    <p style="margin: 5px 0; color: white;"><strong>Note moyenne :</strong> {movie['vote_average']}/10</p>
                    <h6 style="margin: 5px 0; color: white;">Synopsis :</h6>
                    <p style="color: white;">{movie['overview'][:100]}...</p>  <!-- Limiter le texte du synopsis -->
                    <a href="https://embed.su/embed/movie/{movie['id']}" target="_blank" style="text-decoration: none;">
                        <button style="padding: 2px 50px; font-size: 16px; background-color: #0e1117; color: white; border: none; border-radius: 5px; cursor: pointer;">
                            Voir
                        </button>
                    </a>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
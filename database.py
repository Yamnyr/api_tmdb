import sqlite3
import pandas as pd
import streamlit as st

DATABASE = "movies.db"

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
    return conn

def insert_into_db(df):
    conn = create_connection(DATABASE)

    if conn is not None:
        try:
            with conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS movies (
                        id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        release_date TEXT,
                        genres TEXT,
                        popularity REAL,
                        vote_average REAL,
                        poster_url TEXT,
                        overview TEXT
                    )
                ''')
            df['genres'] = df['genres'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

            existing_ids = conn.execute('SELECT id FROM movies').fetchall()
            existing_ids_set = set(row[0] for row in existing_ids)

            new_movies_df = df[~df['id'].isin(existing_ids_set)]

            if new_movies_df.empty:
                st.warning("Tous les films sont déjà présents dans la base de données.")
            else:
                new_movies_df.to_sql('movies', conn, if_exists='append', index=False)
                st.success(f"{len(new_movies_df)} films insérés dans la base de données.")

        except sqlite3.Error as e:
            st.error(f"Erreur lors de l'insertion dans la base de données : {e}")
        finally:
            conn.close()
    else:
        st.error("Erreur : Impossible de créer la connexion à la base de données.")

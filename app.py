import streamlit as st
import pickle
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

# Function to fetch movie poster
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    response = requests.get(url)
    data = response.json()
    return "https://image.tmdb.org/t/p/w500" + data['poster_path']


# def fetch_overview(movie_id):
#     url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
#     response = requests.get(url)
#     overview = response.json()
#     return overview.get("overview", "No overview available.")

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    response = requests.get(url)
    data = response.json()

    genres = ", ".join([genre['name'] for genre in data.get("genres", [])])
    vote_count = data.get("vote_count", "N/A")
    revenue = data.get("revenue", 0)
    runtime = data.get("runtime", "N/A")
    overview = data.get("overview", "No overview available.")
    
    return {
        "genres": genres,
        "vote_count": vote_count,
        "revenue": f"${revenue:,.0f}",
        "runtime": f"{runtime} min",
        "overview": overview
    }



# Function to recommend movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    recommended_details  = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
        recommended_details .append(fetch_movie_details(movie_id))
    return recommended_movies, recommended_posters, recommended_details 

# Load data
similarity = pickle.load(open('similarity.pkl', 'rb'))
movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movie_dict)

# Streamlit UI
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Get suggestions based on your favorite movie!</p>", unsafe_allow_html=True)

selected_movie = st.selectbox("🎥 Select a movie you like:", movies['title'].values)

if st.button("Recommend 🎯"):
    with st.spinner("🔍 Please wait !!!"):
        names, posters, details = recommend(selected_movie)

    st.markdown("### 🏆 Top 5 Movies You May Like")

    for i in range(5):
        with st.container():
            cols = st.columns([1, 2])
            with cols[0]:
                st.image(posters[i], use_container_width=True)
            with cols[1]:
                st.markdown(f"**🎬 {names[i]}**", unsafe_allow_html=True)
                st.markdown(f"**📝 Overview:** {details[i]['overview']}", unsafe_allow_html=True)
                st.markdown("---")
                st.markdown(f"🎭 **Genres:** {details[i]['genres']}")
                st.markdown(f"🗳️ **Vote Count:** {details[i]['vote_count']}")
                st.markdown(f"💸 **Revenue:** {details[i]['revenue']}")
                st.markdown(f"⏱️ **Runtime:** {details[i]['runtime']}")
        st.markdown("---")


  
    st.markdown("Thank you for using !!!")

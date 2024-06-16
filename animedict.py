import streamlit as st
import requests
import pandas as pd
import altair as alt

# Function to fetch anime information from the Kitsu API
def get_anime_info(anime_title):
    base_url = "https://kitsu.io/api/edge/anime"
    params = {"filter[text]": anime_title}
    
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: Unable to retrieve anime information. Status code: {response.status_code}")
        return None

# Function to display anime information
def display_anime_info(anime_info, show_image, show_popularity_rank):
    if anime_info:
        st.subheader("Anime Information")
        st.write(f"**Title:** {anime_info['data'][0]['attributes']['titles']['en']}")
        st.write(f"**Synopsis:** {anime_info['data'][0]['attributes']['synopsis']}")
        st.write(f"**Episode Count:** {anime_info['data'][0]['attributes']['episodeCount']}")
        st.write(f"**Average Rating:** {anime_info['data'][0]['attributes']['averageRating']}")
        
        if show_popularity_rank:
            st.write(f"**Popularity Rank:** {anime_info['data'][0]['attributes']['popularityRank']}")
        
        if show_image:
            st.image(anime_info['data'][0]['attributes']['posterImage']['original'], caption="Anime Poster", use_column_width=True)
        else:
            st.write("Image not displayed.")
    else:
        st.warning("Please enter a valid anime title.")

# Function to generate a chart showing the highest or lowest-rated episodes for a specific anime
def generate_episode_chart(anime_title, sort_order="-averageRating"):
    base_url = "https://kitsu.io/api/edge/anime"
    params = {"filter[text]": anime_title, "page[limit]": 10, "sort": sort_order}  # Adjusted page[limit] for a larger sample

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        anime_data = response.json()['data']
        
        if not anime_data:
            st.warning(f"No anime found with the title: {anime_title}")
            return None

        titles = []
        ratings = []

        for anime in anime_data:
            title = anime['attributes']['titles'].get('en', 'N/A')
            episodes = anime['attributes'].get('episodeCount', 'N/A')
            rating = anime['attributes']['averageRating']

            titles.append(f"{title} (Episodes: {episodes})")
            ratings.append(rating)

        df = pd.DataFrame({'Anime': titles, 'Average Rating': ratings})
        chart = alt.Chart(df).mark_bar().encode(
            x='Average Rating:Q',
            y='Anime:N',
            color='Anime:N',
            tooltip=['Anime:N', 'Average Rating:Q']
        )
        return chart
    else:
        st.error(f"Error: Unable to retrieve anime information. Status code: {response.status_code}")
        return None

# Main Streamlit app
st.title("Anime Information Explorer ♦️")
st.write("The 'Anime Information Explorer' program is a Streamlit web application that allows users to explore details about anime. Users can input the title of an anime and receive information such as the title, synopsis, episode count, and average rating. The program also provides options to toggle the display of anime posters/images. The user-friendly interface, powered by the Kitsu API, enhances the experience of discovering and learning about different anime titles.")

# Importance message about user input
st.write("**Important: Please enter the exact name of the anime and avoid using abbreviated versions to ensure all features function properly.**")

# Sidebar for filtering options
st.sidebar.header("Filter")
anime_title = st.text_input("Enter Anime Title:")

# Button to toggle image display
show_image = st.sidebar.button("Toggle Image Display", True)

# Checkbox to toggle popularity rank display
show_popularity_rank = st.sidebar.checkbox("Show Popularity Rank")

# Fetch anime information based on user input and sidebar selections
anime_info = get_anime_info(anime_title)

# Display anime information if it exists
if anime_title:
    # Toggle image display based on button click
    display_anime_info(anime_info, show_image, show_popularity_rank)

# Button to generate a chart showing the highest-rated episodes for a specific anime
if st.button("Generate Highest-Rated Episode Chart"):
    episode_chart = generate_episode_chart(anime_title, sort_order="-averageRating")
    if episode_chart:
        st.subheader(f"Highest-Rated Episodes for {anime_title}")
        st.altair_chart(episode_chart, use_container_width=True)

# Button to generate a chart showing the lowest-rated episodes for a specific anime
if st.button("Generate Lowest-Rated Episode Chart"):
    episode_chart_lowest = generate_episode_chart(anime_title, sort_order="averageRating")
    if episode_chart_lowest:
        st.subheader(f"Lowest-Rated Episodes for {anime_title}")
        st.altair_chart(episode_chart_lowest, use_container_width=True)

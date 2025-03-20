import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---- Streamlit Configuration ----
st.set_page_config(page_title="GFlix Streaming Dashboard", layout="wide")

# ---- Custom Styling ----
st.header("GFlix Streaming Dashboard")
st.markdown("""---""")

# ---- Load Cleaned CSV Files ----
@st.cache_data
def load_data():
    users = pd.read_csv("cleaned_users.csv")
    subscriptions = pd.read_csv("cleaned_subscriptions.csv")
    watch_history = pd.read_csv("cleaned_watch_history.csv")
    movies = pd.read_csv("cleaned_movies.csv")
    ratings = pd.read_csv("cleaned_ratings.csv")
    return users, subscriptions, watch_history, movies, ratings

users_df, subscriptions_df, watch_history_df, movies_df, ratings_df = load_data()

# ---- USER & SUBSCRIPTION STATS ----
st.subheader("User & Subscription Insights")

col1, col2, col3 = st.columns(3)

# Total Users
total_users = users_df.shape[0]
col1.metric("Total Users", total_users)

# Active Subscriptions
active_subs = subscriptions_df[subscriptions_df["churn_status"] == "active"].shape[0]
col2.metric("Active Subscriptions", active_subs)

# Churn Rate Calculation
churn_rate = (subscriptions_df[subscriptions_df["churn_status"] == "churned"].shape[0] / total_users) * 100
col3.metric("Churn Rate (%)", round(churn_rate, 2))

st.markdown("""---""")

#

# ---- CHURN RATE BY SUBSCRIPTION PLAN ----
st.subheader("Churn Rate by Subscription Plan")

# Calculate churn rate per plan
churn_rate_plan = subscriptions_df.groupby("plan_type").apply(lambda x: (x["churn_status"] == "churned").sum() / len(x) * 100).reset_index(name="churn_rate")

# Streamlit bar chart
st.bar_chart(churn_rate_plan.set_index("plan_type")[["churn_rate"]])

st.markdown("""---""")

import numpy as np

# ---- Movie Dropdown ----
st.subheader("Select a Movie to Analyze Watch Trends Across Devices")

# Get unique movie names sorted alphabetically
movie_options = movies_df.sort_values("title")["title"].unique()
selected_movie = st.selectbox("Choose a Movie:", movie_options)

# Get the corresponding movie_id
selected_movie_id = movies_df[movies_df["title"] == selected_movie]["movie_id"].values[0]

# Filter Data Based on Selected Movie
filtered_watch_history = watch_history_df[watch_history_df["movie_id"] == selected_movie_id]

# Calculate Average Watch Duration Per Device
movie_watch_duration_by_device = (
    filtered_watch_history.groupby("device_type")["watch_duration"].mean().reset_index()
)

# ✅ Ensure "Mobile", "Laptop", and "Smart TV" always appear (fill missing with 0)
required_devices = ["Mobile", "Laptop", "Smart TV"]
for device in required_devices:
    if device not in movie_watch_duration_by_device["device_type"].values:
        movie_watch_duration_by_device = pd.concat(
            [movie_watch_duration_by_device, pd.DataFrame({"device_type": [device], "watch_duration": [0]})],
            ignore_index=True
        )

# Sort devices for consistency
movie_watch_duration_by_device = movie_watch_duration_by_device.sort_values(by="watch_duration", ascending=True)

# Display Results
st.subheader(f"Avg Watch Duration Per Device for '{selected_movie}'")

# Streamlit horizontal bar chart
st.bar_chart(movie_watch_duration_by_device.set_index("device_type")[["watch_duration"]], use_container_width=True)


st.markdown("""---""")


# ---- Movie Dropdown for Ratings ----
st.subheader("Select a Movie to See Ratings & Reviews")

# Get unique movie names sorted alphabetically
movie_options = movies_df.sort_values("title")["title"].unique()
selected_movie = st.selectbox("Choose a Movie for Ratings:", movie_options, key="rating_movie")

# Get the corresponding movie_id
selected_movie_id = movies_df[movies_df["title"] == selected_movie]["movie_id"].values[0]

# ---- Calculate Average Rating ----
movie_avg_rating = ratings_df[ratings_df["movie_id"] == selected_movie_id]["rating"].mean()

# Display Average Rating
st.subheader(f"Average Rating for '{selected_movie}': {round(movie_avg_rating, 2) if not pd.isna(movie_avg_rating) else 'No Ratings Yet'}")

# ---- Show Latest Reviews for Selected Movie ----
st.subheader("Latest User Reviews")

# Filter reviews for the selected movie
latest_reviews = (
    ratings_df[ratings_df["movie_id"] == selected_movie_id]
    .merge(users_df, on="user_id")
    .merge(movies_df, on="movie_id")
    .sort_values(by="review_date", ascending=False)
    .head(10)
)

# ✅ Check Actual Column Names


# ✅ Rename Correctly Based on Actual Column Names
latest_reviews = latest_reviews.rename(columns={"name": "User Name", "title": "Movie Title", "rating": "Rating", "review_date": "Review Date"})

# ✅ Show DataFrame Only If It Has Data
if latest_reviews.empty:
    st.info("No reviews available for this movie yet.")
else:
    st.dataframe(latest_reviews[["User Name", "Movie Title", "Rating", "Review Date"]])

st.markdown("""---""")


import pandas as pd
import streamlit as st

# Assuming 'watch_history_df' contains movie watch logs
# Assuming 'movies_df' contains movie details including genres

st.subheader("📊 Genre Popularity Over Time")

# Convert watch date to datetime format if not already
watch_history_df["watch_date"] = pd.to_datetime(watch_history_df["watch_date"])

# Extract month-year for grouping
watch_history_df["month_year"] = watch_history_df["watch_date"].dt.to_period("M")

# Merge watch history with movie genres
watch_data = watch_history_df.merge(movies_df, on="movie_id")

# Group by month-year and genre, then count watches
genre_trends = watch_data.groupby(["month_year", "genre"]).size().reset_index(name="watch_count")

# Pivot table to format data for plotting
genre_trends_pivot = genre_trends.pivot(index="month_year", columns="genre", values="watch_count").fillna(0)

# Convert period index to string for Streamlit compatibility
genre_trends_pivot.index = genre_trends_pivot.index.astype(str)

# Display line chart
st.line_chart(genre_trends_pivot)


st.markdown("""---""")
import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Streamlit Configuration ----
st.set_page_config(page_title="GFlix Streaming Dashboard", layout="wide")

# ---- Load Data ----
@st.cache_data
def load_data():
    users = pd.read_csv("cleaned_users.csv")
    subscriptions = pd.read_csv("cleaned_subscriptions.csv")
    watch_history = pd.read_csv("cleaned_watch_history.csv")
    movies = pd.read_csv("cleaned_movies.csv")
    ratings = pd.read_csv("cleaned_ratings.csv")
    country_coords = pd.read_csv("country_coordinates.csv")  # Load country coordinates
    return users, subscriptions, watch_history, movies, ratings, country_coords

users_df, subscriptions_df, watch_history_df, movies_df, ratings_df, country_coords_df = load_data()

# ---- Sidebar for Navigation ----
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a Page", ["General Dashboard", "Movie-Specific Analysis"])

# ---- General Dashboard ----
if page == "General Dashboard":
    st.title("📊 GFlix General Dashboard")

    # ---- USER & SUBSCRIPTION STATS ----
    st.subheader("📊 User & Subscription Insights")

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

    # ---- CHURN RATE BY SUBSCRIPTION PLAN ----
    st.subheader("📉 Churn Rate by Subscription Plan")

    # Calculate churn rate per plan
    churn_rate_plan = subscriptions_df.groupby("plan_type").apply(lambda x: (x["churn_status"] == "churned").sum() / len(x) * 100).reset_index(name="churn_rate")

    # Streamlit bar chart
    st.bar_chart(churn_rate_plan.set_index("plan_type")[["churn_rate"]])

    st.markdown("""---""")

    # ---- TOTAL REVENUE ----
    st.subheader("💰 Total Revenue & Revenue by Subscription Plan")

    # Fixing column name issue (using 'amount' from schema)
    total_revenue = subscriptions_df["amount"].sum()
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

    # Revenue by Plan Type
    revenue_by_plan = subscriptions_df.groupby("plan_type")["amount"].sum().reset_index()

    # Display bar chart
    st.bar_chart(revenue_by_plan.set_index("plan_type"))

    st.markdown("""---""")

    # ---- RETENTION RATE ----
    st.subheader("🔄 Retention Rate by Subscription Plan")

    # Calculate Retention Rate (Renewed Subscriptions / Total Subscriptions)
    retention_rate_plan = subscriptions_df.groupby("plan_type").apply(lambda x: (x["renewed"] == True).sum() / len(x) * 100).reset_index(name="retention_rate")

    # Streamlit bar chart
    st.bar_chart(retention_rate_plan.set_index("plan_type")[["retention_rate"]])

    st.markdown("""---""")

    # ---- GENRE POPULARITY OVER TIME ----
    st.subheader("📊 Genre Popularity Over Time")

    # Convert watch date to datetime
    watch_history_df["watch_date"] = pd.to_datetime(watch_history_df["watch_date"])
    watch_history_df["month_year"] = watch_history_df["watch_date"].dt.to_period("M")

    # Merge with movies
    watch_data = watch_history_df.merge(movies_df, on="movie_id")

    # Group by month-year and genre
    genre_trends = watch_data.groupby(["month_year", "genre"]).size().reset_index(name="watch_count")

    # Pivot table
    genre_trends_pivot = genre_trends.pivot(index="month_year", columns="genre", values="watch_count").fillna(0)
    genre_trends_pivot.index = genre_trends_pivot.index.astype(str)

    # Display line chart
    st.line_chart(genre_trends_pivot)

    st.markdown("""---""")

    # ---- INTERACTIVE WORLD MAP ----
    st.subheader("🌍 Subscription Plans Distribution by Country")

    subscriptions_by_country = (
        users_df.merge(subscriptions_df, on="user_id")
        .groupby(["country", "plan_type"])["payment_id"]
        .count()
        .reset_index()
        .rename(columns={"payment_id": "subscription_count"})
    )

    # Merge with country coordinates
    subscriptions_by_country = subscriptions_by_country.merge(country_coords_df, on="country", how="left")

    # Create interactive world map
    fig = px.scatter_geo(
        subscriptions_by_country,
        lat="lat",
        lon="lon",
        text="country",
        size="subscription_count",
        color="plan_type",
        hover_name="country",
        hover_data={"subscription_count": True, "plan_type": True, "lat": False, "lon": False},
        projection="natural earth",
        title="GFlix Subscription Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---- DEMOGRAPHIC AREA-WISE SUBSCRIPTION TABLE ----
    st.subheader("📋 Subscription Breakdown by Country & Plan")

    # Pivot table for better readability
    subscription_table = subscriptions_by_country.pivot(index="country", columns="plan_type", values="subscription_count").fillna(0)

    # Convert to integer format
    subscription_table = subscription_table.astype(int)

    # Display table in Streamlit
    st.dataframe(subscription_table)

# ---- Movie-Specific Analysis ----
elif page == "Movie-Specific Analysis":
    st.title("🎬 Movie-Specific Analysis")

    # Movie selection dropdown
    movie_options = movies_df.sort_values("title")["title"].unique()
    selected_movie = st.selectbox("Choose a Movie:", movie_options)

    # Get movie_id and runtime
    selected_movie_data = movies_df[movies_df["title"] == selected_movie]
    selected_movie_id = selected_movie_data["movie_id"].values[0]
    movie_runtime = selected_movie_data["runtime"].values[0]  # Runtime in minutes

    # ---- WATCH TRENDS BY DEVICE ----
    st.subheader("📺 Watch Trends by Device")

    # Filter Data Based on Selected Movie
    filtered_watch_history = watch_history_df[watch_history_df["movie_id"] == selected_movie_id]

    # Calculate Average Watch Duration Per Device
    watch_duration_by_device = filtered_watch_history.groupby("device_type")["watch_duration"].mean().reset_index()

    # Ensure "Mobile", "Laptop", "Smart TV" always appear (fill missing with 0)
    required_devices = ["Mobile", "Laptop", "Smart TV"]
    for device in required_devices:
        if device not in watch_duration_by_device["device_type"].values:
            watch_duration_by_device = pd.concat(
                [watch_duration_by_device, pd.DataFrame({"device_type": [device], "watch_duration": [0]})],
                ignore_index=True
            )

    # Display bar chart
    st.bar_chart(watch_duration_by_device.set_index("device_type")[["watch_duration"]])

    st.markdown("""---""")

    # ---- MOVIE RATINGS & REVIEWS ----
    st.subheader("⭐ Movie Ratings & Reviews")

    # Calculate Average Rating
    movie_avg_rating = ratings_df[ratings_df["movie_id"] == selected_movie_id]["rating"].mean()

    # Display Average Rating
    st.metric(f"Average Rating for '{selected_movie}'", round(movie_avg_rating, 2) if not pd.isna(movie_avg_rating) else "No Ratings Yet")

    # Show Latest Reviews
    latest_reviews = (
        ratings_df[ratings_df["movie_id"] == selected_movie_id]
        .merge(users_df, on="user_id")
        .merge(movies_df, on="movie_id")
        .sort_values(by="review_date", ascending=False)
        .head(10)
    )

    # Rename for readability
    latest_reviews = latest_reviews.rename(columns={"name": "User Name", "title": "Movie Title", "rating": "Rating", "review_date": "Review Date"})

    if latest_reviews.empty:
        st.info("No reviews available for this movie yet.")
    else:
        st.dataframe(latest_reviews[["User Name", "Movie Title", "Rating", "Review Date"]])

    st.markdown("""---""")

    # ---- MOVIE ENGAGEMENT ANALYSIS ----
    st.subheader("🎬 Movie Engagement Rate by Subscription Plan")

    # Merge watch history with subscriptions
    watch_with_subs = (
        watch_history_df[watch_history_df["movie_id"] == selected_movie_id]
        .merge(users_df, on="user_id")
        .merge(subscriptions_df, on="user_id")
    )

    # Calculate engagement rate
    engagement_by_plan = (
        watch_with_subs.groupby("plan_type")["watch_duration"]
        .mean()
        .reset_index()
        .rename(columns={"watch_duration": "avg_watch_time"})
    )

    # Compute Engagement Rate
    engagement_by_plan["engagement_rate (%)"] = (engagement_by_plan["avg_watch_time"] / movie_runtime) * 100

    # Display engagement rate table
    st.subheader(f"📊 Engagement Rate for '{selected_movie}' by Subscription Plan")
    st.dataframe(engagement_by_plan[["plan_type", "engagement_rate (%)"]])

    # Overall Engagement Rate Calculation
    total_watch_time = watch_history_df[watch_history_df["movie_id"] == selected_movie_id]["watch_duration"].sum()
    total_watches = watch_history_df[watch_history_df["movie_id"] == selected_movie_id]["watch_id"].count()
    overall_avg_watch_time = total_watch_time / total_watches if total_watches > 0 else 0
    overall_engagement_rate = (overall_avg_watch_time / movie_runtime) * 100

    st.subheader(f"📌 Overall Engagement Rate for '{selected_movie}': **{round(overall_engagement_rate, 2)}%**")

    st.markdown("""---""")

    # ---- AGE GROUP ANALYSIS FOR SELECTED MOVIE ----
    st.subheader("👥 Age Group Percentage for Selected Movie")

    # Merge watch history with users to get ages
    watch_with_age = (
        watch_history_df[watch_history_df["movie_id"] == selected_movie_id]
        .merge(users_df, on="user_id", how="left")
    )

    # Check if data is available
    if watch_with_age.empty:
        st.warning(f"No age data available for '{selected_movie}'.")
    else:
        # Define age groups
        age_bins = [0, 18, 25, 35, 45, 60, 100]
        age_labels = ["<18", "18-24", "25-34", "35-44", "45-59", "60+"]
        
        # Ensure 'age' column is numeric
        watch_with_age["age"] = pd.to_numeric(watch_with_age["age"], errors="coerce")
        
        # Drop rows where age is NaN
        watch_with_age = watch_with_age.dropna(subset=["age"])
        
        # Assign age groups
        watch_with_age["age_group"] = pd.cut(watch_with_age["age"], bins=age_bins, labels=age_labels, right=False)
        
        # Calculate percentage of each age group
        age_group_percentage = (
            watch_with_age["age_group"]
            .value_counts(normalize=True)
            .mul(100)
            .reset_index()
            .rename(columns={"index": "Age Group", "age_group": "age"})
        )

        # Display age group percentage table
        st.subheader(f"📊 Age Group Percentage for '{selected_movie}'")
        st.dataframe(age_group_percentage)

    st.markdown("""---""")
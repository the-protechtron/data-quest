import pandas as pd

# Load the datasets
ratings_path = "ratings.csv"
users_path = "cleaned_users.csv"
movies_path = "cleaned_movies.csv"

df = pd.read_csv(ratings_path)
users_df = pd.read_csv(users_path)
movies_df = pd.read_csv(movies_path)

# 1. Remove rows with missing values
df.dropna(inplace=True)

# 2. Convert 'review_date' column to datetime format
df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')

# 3. Keep only ratings within the valid range (0-5)
df = df[(df['rating'] >= 0) & (df['rating'] <= 5)]

# 4. Keep only rows with valid user_id and movie_id
df = df[df['user_id'].isin(users_df['user_id'])]
df = df[df['movie_id'].isin(movies_df['movie_id'])]

# 5. Remove duplicate entries
df.drop_duplicates(inplace=True)

# 6. Save cleaned dataset
cleaned_file_path = "cleaned_ratings.csv"
df.to_csv(cleaned_file_path, index=False)

print(f"Cleaned dataset saved to {cleaned_file_path}")

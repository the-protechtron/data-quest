import pandas as pd

# Load the datasets
watch_history_path = "watch_history.csv"
users_path = "cleaned_users.csv"
movies_path = "cleaned_movies.csv"

df = pd.read_csv(watch_history_path)
users_df = pd.read_csv(users_path)
movies_df = pd.read_csv(movies_path)

# 1. Remove rows with missing values
df.dropna(inplace=True)

# 2. Convert 'watch_date' column to datetime format
df['watch_date'] = pd.to_datetime(df['watch_date'], errors='coerce')

# 3. Keep only allowed device types
df = df[df['device_type'].isin(["Laptop", "Smart TV", "Mobile"])]

# 4. Remove rows where watch_duration is negative or greater than 270
df = df[(df['watch_duration'] >= 0) & (df['watch_duration'] <= 270)]

# 5. Keep only rows with valid user_id and movie_id
df = df[df['user_id'].isin(users_df['user_id'])]
df = df[df['movie_id'].isin(movies_df['movie_id'])]

# 6. Remove duplicate entries
df.drop_duplicates(inplace=True)

# 7. Save cleaned dataset
cleaned_file_path = "cleaned_watch_history.csv"
df.to_csv(cleaned_file_path, index=False)


print(f"Cleaned dataset saved to {cleaned_file_path}")

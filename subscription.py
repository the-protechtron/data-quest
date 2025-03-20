import pandas as pd

# Load the CSV file
df = pd.read_csv("movies.csv")

# Remove rows with NULL values
df.dropna(subset=["movie_id", "title", "release_year", "runtime", "genre"], inplace=True)

# Group by movie_id to retain unique IDs, but merge genres
cleaned_df = df.groupby(["movie_id", "title", "release_year", "runtime"], as_index=False).agg(
    {"genre": lambda x: ", ".join(sorted(set(x)))}
)

# Sort the cleaned data
cleaned_df.sort_values(by=["release_year", "runtime", "title"], inplace=True)

# Save to CSV
cleaned_df.to_csv("cleaned_movies.csv", index=False)

# Display result
print(cleaned_df.head())
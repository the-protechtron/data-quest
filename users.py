import pandas as pd
import pycountry

# Load the dataset
file_path = "users.csv"
df = pd.read_csv(file_path)

# 1. Remove rows with missing values
df.dropna(inplace=True)

# 2. Convert 'date' column to datetime format
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# 3. Validate email format (removes invalid emails)
df = df[df['email'].str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', na=False)]

# 4. Remove emails with two adjacent dots ("..")
df = df[~df['email'].str.contains(r'\.\.', regex=True)]

# 5. Standardize country names (remove extra spaces)
df['country'] = df['country'].str.strip().str.title()

# 6. Control age between 1-100
df = df[(df['age'] >= 1) & (df['age'] <= 100)]

# 7. Get the full list of valid countries using pycountry
valid_countries = [country.name for country in pycountry.countries]

# 8. Filter valid country names
df = df[df['country'].isin(valid_countries)]

# 9. Remove duplicate user_id entries (keep the first occurrence)
df.drop_duplicates(subset=['user_id'], keep='first', inplace=True)

# 10. Set user_id as the index (acting as the primary key)
# df.set_index('user_id', inplace=True)

# Save cleaned dataset
cleaned_file_path = "cleaned_users.csv"
df.to_csv(cleaned_file_path, index=False)

print(f"Cleaned dataset saved to {cleaned_file_path}")

import pandas as pd
import mysql.connector
from datetime import datetime
from logins import MySQL

host, user, password, database = MySQL()

conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

cursor = conn.cursor()


df = pd.read_csv("netflix_titles.csv")
df.drop(columns=["show_id"], inplace=True)
df.dropna(subset=['date_added'], inplace=True)

def convert_date(date_str):
    date_object = datetime.strptime(date_str.strip(), "%B %d, %Y")
    return date_object.strftime("%Y-%m-%d")

df["date_added"] = df["date_added"].apply(convert_date)

for index, row in df.iterrows():
    query = """
    INSERT INTO content (type1, title, director, cast, country, date_added, release_year, rating, duration, listed_in, description)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    if type(row["duration"]) != str:  # edge case
        row["duration"] = row["rating"]
        row["rating"] = None

    values = (row['type'], row['title'], row['director'], row['cast'], row['country'], row['date_added'],
              row['release_year'], row['rating'], row['duration'], row['listed_in'], row['description'])
    cursor.execute(query, values)


conn.commit()

cursor.close()
conn.close()
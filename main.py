import requests
import psycopg2
from pandas import json_normalize

# -------------------------------
#   PostgreSQL
# -------------------------------
web_url = "https://api.divar.ir/v1/places/cities"
database = "Divar"
connection_string = f"dbname={database} user=postgres password=123456 host=localhost port=5432"


# -------------------------------
#   Functions
# -------------------------------
def fetch_divar_cities(url: str):
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    df = json_normalize(data["cities"])[[
        "id", "name", "slug", "radius",
        "default_location.latitude",
        "default_location.longitude"
    ]]

    df.columns = ["ID", "Name", "Slug", "Radius", "Latitude", "Longitude"]
    return df


def create_table():
    try:
        with psycopg2.connect(connection_string) as con:
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS Cities CASCADE;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Cities (
                        ID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        Name TEXT NOT NULL,
                        Slug TEXT NOT NULL,
                        Radius INT,
                        Latitude FLOAT,
                        Longitude FLOAT
                    );
            """)

    except Exception as ex:
        print(ex)


def save_to_db(items, con):
    cur = con.cursor()
    for item in items.values:
        cur.execute(
            "INSERT INTO Cities(Name,Slug,Radius,Latitude,Longitude) "
            "VALUES(%s,%s,%s,%s,%s)",
            (
                item[1],
                item[2],
                item[3],
                item[4],
                item[5]
            )
        )


# -------------------------------
#   Main program
# -------------------------------
create_table()

with psycopg2.connect(connection_string) as con:
    con.autocommit = True
    items = fetch_divar_cities(web_url)
    save_to_db(items, con)

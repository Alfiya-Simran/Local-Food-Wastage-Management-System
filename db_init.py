import sqlite3
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'dataset'
DB_PATH = DATA_DIR / 'food_wastage.db'


def create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS providers (
            Provider_ID INTEGER PRIMARY KEY,
            Name TEXT,
            Type TEXT,
            Address TEXT,
            City TEXT,
            Contact TEXT
        );'''
    )
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS receivers (
            Receiver_ID INTEGER PRIMARY KEY,
            Name TEXT,
            Type TEXT,
            City TEXT,
            Contact TEXT
        );'''
    )
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS food_listings (
            Food_ID INTEGER PRIMARY KEY,
            Food_Name TEXT,
            Quantity INTEGER,
            Expiry_Date TEXT,
            Provider_ID INTEGER,
            Provider_Type TEXT,
            Location TEXT,
            Food_Type TEXT,
            Meal_Type TEXT
        );'''
    )
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS claims (
            Claim_ID INTEGER PRIMARY KEY,
            Food_ID INTEGER,
            Receiver_ID INTEGER,
            Status TEXT,
            Timestamp TEXT
        );'''
    )
    conn.commit()


def load_csvs(conn: sqlite3.Connection) -> None:
    providers_csv = DATA_DIR / 'providers_data.csv'
    receivers_csv = DATA_DIR / 'receivers_data.csv'
    listings_csv = DATA_DIR / 'food_listings_data.csv'
    claims_csv = DATA_DIR / 'claims_data.csv'

    if providers_csv.exists():
        df = pd.read_csv(providers_csv)
        df.to_sql('providers', conn, if_exists='replace', index=False)
    if receivers_csv.exists():
        df = pd.read_csv(receivers_csv)
        df.to_sql('receivers', conn, if_exists='replace', index=False)
    if listings_csv.exists():
        df = pd.read_csv(listings_csv)
        df.to_sql('food_listings', conn, if_exists='replace', index=False)
    if claims_csv.exists():
        df = pd.read_csv(claims_csv)
        df.to_sql('claims', conn, if_exists='replace', index=False)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        create_tables(conn)
        load_csvs(conn)
    print(f"Database initialized at: {DB_PATH}")


if __name__ == '__main__':
    main()


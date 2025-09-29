import sqlite3
import pandas as pd
import io
import streamlit as st
import datetime

# Connect to SQLite database and load data
@st.cache_data
def load_data_from_db():
    # Adjust the path to your SQLite file
    conn = sqlite3.connect("cars_db.sqlite")  
    query = "SELECT link, title, price, engine, fuel, mileage, color, gearbox, paper, brand, year, model, finition, location, wilaya, date FROM cars"
    data = pd.read_sql(query, conn)
    conn.close()
    return data

# Clean the data
def clean_data(data):
    # Drop rows where 'brand' or 'model' is empty (NaN or empty string)
    cleaned_data = data.dropna(subset=['brand', 'model'])  # Drop rows where brand or model is NaN
    cleaned_data = cleaned_data[cleaned_data['brand'].str.strip() != '']  # Remove rows with empty string in 'brand'
    cleaned_data = cleaned_data[cleaned_data['model'].str.strip() != '']  # Remove rows with empty string in 'model'

    # Remove rows where the number of occurrences of a brand is less than 20
    cleaned_data = cleaned_data.groupby('model').filter(lambda x: len(x) >= 20)
    cleaned_data = cleaned_data.groupby('brand').filter(lambda x: len(x) >= 20)

    # Convert 'date' column to datetime
    cleaned_data['date'] = pd.to_datetime(cleaned_data['date'])

    # Filter the data where the 'date' is greater than 2020-01-01
    cleaned_data = cleaned_data[cleaned_data['date'] > '2020-01-01']

    cleaned_data = cleaned_data[cleaned_data['price']>49]

    cleaned_data = cleaned_data[cleaned_data['mileage']>=0]

    # Define the list of unwanted prices
    bad_prices = [
        123, 
        111, 1111, 11111,
        222, 2222, 22222,
        333, 3333, 33333,
        444, 4444, 44444,
        55, 555, 5555, 55555,
        66, 666, 6666, 66666,
        77, 777, 7777, 77777,
        88, 888, 8888, 88888,
        99, 999, 9999, 99999
    ]

    # Remove rows where price is in that list
    cleaned_data = cleaned_data[~cleaned_data['price'].isin(bad_prices)]

    # Current year
    current_year = datetime.datetime.now().year

    # If mileage < 1000 and year != current year → multiply mileage * 1000
    cleaned_data.loc[(cleaned_data["mileage"] < 1000) & (cleaned_data["year"] != current_year), "mileage"] *= 1000

    # Convert all model names to uppercase
    cleaned_data["model"] = cleaned_data["model"].str.upper()
    
    return cleaned_data

def convert_df_to_excel(df):
    """
    Convert a DataFrame to an Excel file stored in memory for download.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Car Data")
    return output.getvalue()
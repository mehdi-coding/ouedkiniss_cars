import sqlite3
import pandas as pd
import io
import streamlit as st

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

    return cleaned_data

def convert_df_to_excel(df):
    """
    Convert a DataFrame to an Excel file stored in memory for download.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Car Data")
    return output.getvalue()
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sqlite3
import io
import mplcursors
import plotly.express as px

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
    # cleaned_data = cleaned_data[cleaned_data['date'] > '2020-01-01']

    cleaned_data = cleaned_data[cleaned_data['price']>49]

    cleaned_data = cleaned_data[cleaned_data['mileage']>=0]

    # Ensure only integer values in the 'year' column
    cleaned_data['year'] = pd.to_numeric(cleaned_data['year'], errors='coerce')
    cleaned_data = cleaned_data.dropna(subset=['year'])  # Drop rows where 'year' is NaN
    cleaned_data['year'] = cleaned_data['year'].astype(int)  # Convert 'year' to integers

    # Ensure only integer values in the 'mileage' column
    cleaned_data['mileage'] = pd.to_numeric(cleaned_data['mileage'], errors='coerce')
    cleaned_data = cleaned_data.dropna(subset=['mileage'])  # Drop rows where 'mileage' is NaN
    cleaned_data['mileage'] = cleaned_data['mileage'].astype(int)  # Convert 'mileage' to integers

    cleaned_data['mileage'] = cleaned_data['mileage'].apply(lambda x: x * 1000 if x < 600 else x)

    cleaned_data['mileage'] = cleaned_data['mileage'].apply(lambda x: x / 10 if x > 600000 else x)

    return cleaned_data

def convert_df_to_excel(df):
    """
    Convert a DataFrame to an Excel file stored in memory for download.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Car Data")
    return output.getvalue()



st.title("Models Analysis")

# Load and clean the data
data = load_data_from_db()
data = clean_data(data)
data['date_int'] = (data['date'] - pd.Timestamp('1970-01-01')) // pd.Timedelta('1D')
# Add a date range filter using Streamlit's date_input
st.sidebar.subheader("Select Date Range")

start = st.sidebar.date_input("From:", data['date'].max() - pd.DateOffset(months=3),min_value=data['date'].min(),max_value=data['date'].max())
end = st.sidebar.date_input("To:", data['date'].max(),min_value=start,max_value=data['date'].max())

data= data[data['date'] >= f"{start}"]
data= data[data['date'] <= f"{end}"]

# ---------------------------------------------------------------------
models_list = pd.DataFrame()
brand =None
model = None

brand = st.selectbox(
    "Select a Brand ...",
    sorted(data['brand'].unique()),
    index=None,
    placeholder="Select a Brand ...",
)


if brand:
    models_list = data[data['brand'] == brand]
    model = st.selectbox(
        "Select a Model ...",
        sorted(models_list['model'].unique()),
        index=None,
        placeholder="Select a Model ...",
        )

if model:
    models_list = models_list[models_list['model'] == model]

    selected_years = st.multiselect(
    "Select Years to include in the boxplot",
    options=models_list['year'].unique(),
    default=sorted(models_list['year'].unique()))
     # Filter data based on selected year
    models_list = models_list[models_list['year'].isin(selected_years)]

    if not models_list.empty:
        if models_list['mileage'].min() == models_list['mileage'].max():
            st.write('Mileage available:', models_list['mileage'].min())
        else:
            # Proceed with the slider
            (min_mileage,max_mileage) = st.slider(
                "Select a range of Mileage", 
                models_list['mileage'].min(), 
                models_list['mileage'].max(),
                (models_list['mileage'].min(), models_list['mileage'].max())
            )
            models_list = models_list[models_list['mileage']>=min_mileage]
            models_list = models_list[models_list['mileage']<=max_mileage]

    if not models_list.empty:
        selected_fuels = st.multiselect(
        "Select Fuel to include in the boxplot",
        options=models_list['fuel'].unique(),
        default=models_list['fuel'].unique())
        # Filter data based on selected fuel
        models_list = models_list[models_list['fuel'].isin(selected_fuels)]
    
    if not models_list.empty:
        selected_gearboxs = st.multiselect(
        "Select Gearbox to include in the boxplot",
        options=models_list['gearbox'].unique(),
        default=models_list['gearbox'].unique())
        # Filter data based on selected gearbox
        models_list = models_list[models_list['gearbox'].isin(selected_gearboxs)]

    if not models_list.empty:
        selected_engines = st.multiselect(
        "Select Engines to include in the boxplot",
        options=models_list['engine'].unique(),
        default=models_list['engine'].unique())
        # Filter data based on selected engine
        models_list = models_list[models_list['engine'].isin(selected_engines)]


    
    


        
if model is not None and brand is not None:
    if not models_list.empty:

        st.write("N° of rows:", models_list.shape[0])

        sns.boxplot(x=models_list['price'])

        fig, ax = plt.subplots()  # Create a matplotlib figure and axis
        sns.boxplot(x=models_list['price'], ax=ax)  # Create a boxplot with seaborn
        ax.set_title('Price Distribution')  # Add a title to the plot

        # Display the plot in Streamlit
        st.pyplot(fig)

    
        # Create a matplotlib figure
        fig, ax = plt.subplots(figsize=(12, 6))  # Adjust size as needed

        # Plot the boxplot
        sns.boxplot(x='year', y='price', data=models_list, ax=ax)
        
        # Customize the plot
        ax.set_title("Price Distribution by Year")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)  # Rotate Year labels for readability

        # Display the plot in Streamlit
        st.pyplot(fig)

        fig, ax = plt.subplots()
        sns.histplot(models_list['price'], kde=True, ax=ax, color='blue')
        ax.set_title("Price Distribution")
        st.pyplot(fig)

        Q1_price = models_list['price'].quantile(0.25)
        Q3_price = models_list['price'].quantile(0.75)
        IQR_price = Q3_price - Q1_price

        Q1_mileage = models_list['mileage'].quantile(0.25)
        Q3_mileage = models_list['mileage'].quantile(0.75)
        IQR_mileage = Q3_mileage - Q1_mileage

        # Filter out outliers
        filtered_models_list = models_list[
            (models_list['price'] >= Q1_price - 1.5 * IQR_price) & 
            (models_list['price'] <= Q3_price + 1.5 * IQR_price) &
            (models_list['mileage'] >= Q1_mileage - 1.5 * IQR_mileage) & 
            (models_list['mileage'] <= Q3_mileage + 1.5 * IQR_mileage)]
        # Scatter plot with Matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(filtered_models_list['mileage'], filtered_models_list['price'], alpha=0.6)
        ax.set_title("Price vs. Mileage")
        ax.set_xlabel("Mileage")
        ax.set_ylabel("Price")
        st.pyplot(fig)

        st.write("Listing of the cars:")
        st.write(models_list)
    else:
        st.write("No data available for the selected.")




# --------------------------------------------------------------
# Provide an option to download the cleaned data
st.header("Export Data")
if st.button("Download Cleaned Data as Excel"):
    excel_data = convert_df_to_excel(models_list)
    st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name="cleaned_car_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Footer
st.write("Built with ❤️ using Streamlit!")


import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sqlite3
import io
import mplcursors
import plotly.express as px
from utils import load_data_from_db, clean_data, convert_df_to_excel


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


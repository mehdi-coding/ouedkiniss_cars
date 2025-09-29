import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from utils import load_data_from_db, clean_data, convert_df_to_excel

# Title
st.title("Welcome Car Price Analysis Data Overview for cars v1.0 29-Sep-2025")

# Data Overview
st.header("Number of Rows available")

# Load and clean the data
data = load_data_from_db()

st.write("All Data:",data.shape[0])

data = clean_data(data)
# Convert the datetime column to an integer (number of days since 1970-01-01)
data['date_int'] = (data['date'] - pd.Timestamp('1970-01-01')) // pd.Timedelta('1D')

st.write("Cleaned Data:",data.shape[0])


# Add a date range filter using Streamlit's date_input
st.sidebar.subheader("Select Date Range")

start = st.sidebar.date_input("From:", data['date'].max() - pd.DateOffset(months=1),min_value=data['date'].min(),max_value=data['date'].max())
end = st.sidebar.date_input("To:", data['date'].max(),start,max_value=data['date'].max())

data= data[data['date'] >= f"{start}"]
data= data[data['date'] <= f"{end}"]

st.write("Filtred Data per Posting Year:",data.shape[0])

# ---------------------------------------------------------------------
# Price range filter
st.subheader("Select Price Range")

min_price = int(data['price'].min())
max_price = int(data['price'].max())

price_range = st.slider(
    "Price Range",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=1
)

# Apply the filter
data = data[(data['price'] >= price_range[0]) & (data['price'] <= price_range[1])]

st.write("Filtered Data after Date & Price Range:", data.shape[0])

# ---------------------------------------------------------------------

st.header("Statistical Summary")

st.write(data.describe().drop(columns=['wilaya']))

# Get the describe output for object columns
object_stats = data.drop(columns=['link', 'paper']).describe(include=['object'])

# Compute custom stats for 'wilaya'
wilaya_stats = {
    'count': data['wilaya'].count(),
    'unique': data['wilaya'].nunique(),
    'top': data['wilaya'].mode()[0] if not data['wilaya'].mode().empty else None,
    'freq': data['wilaya'].value_counts().iloc[0] if not data['wilaya'].value_counts().empty else 0,
}

# Convert wilaya_stats into a DataFrame for consistency
wilaya_df = pd.DataFrame(wilaya_stats, index=['wilaya']).T

# Concatenate the two DataFrames
final_stats = pd.concat([object_stats, wilaya_df], axis=1)

# Display the result with Streamlit
st.write(final_stats)

# st.write(data.describe(include=['object']).drop(columns=['link', 'paper']))
# ------------------------------------------------------------------------
# Count of occurrences per brand
brand_counts = data['brand'].value_counts().reset_index()
brand_counts.columns = ['brand', 'count']  # Rename columns for clarity

# Pivot table for average price per brand
brand_avg_price = data.pivot_table(index='brand', values='price', aggfunc='mean').reset_index()

brand_avg_price.columns =['brand', 'Average Price']

# Merge the two tables on the 'brand' column
merged_data = pd.merge(brand_counts, brand_avg_price, on='brand')

# Display the result
st.write(merged_data)

# -------------------------------------------------
# Count of occurrences per model
model_counts = data['model'].value_counts().reset_index()
model_counts.columns = ['model', 'count']  # Rename columns for clarity

# Pivot table for average price per model
model_avg_price = data.pivot_table(index='model', values='price', aggfunc='mean').reset_index()

model_avg_price.columns =['model', 'Average Price']

# Merge the two tables on the 'model' column
merged_data = pd.merge(model_counts, model_avg_price, on='model')

# Display the result
st.write(merged_data)
# ---------------------------------------

## Price Distribution
st.subheader("Price Distribution")
st.write("Histogram of Car Prices:")
fig, ax = plt.subplots()
sns.histplot(data['price'], kde=True, ax=ax, color='blue')
ax.set_title("Price Distribution")
st.pyplot(fig)

sns.boxplot(x=data['price'])

fig, ax = plt.subplots()  # Create a matplotlib figure and axis
sns.boxplot(x=data['price'], ax=ax)  # Create a boxplot with seaborn
ax.set_title('Price Distribution')  # Add a title to the plot

# Display the plot in Streamlit
st.pyplot(fig)

# ----------------------------------------------------------------------

st.header("Price Distribution by Brand")

top_brands = data['brand'].value_counts().head(5).index.tolist()

# Filter data to avoid clutter if there are too many brands
selected_brands = st.sidebar.multiselect(
    "Select brands to include in the boxplot",
    options=data['brand'].unique(),
    default=top_brands  # Default to the first 5 brands
)

# Filter data based on selected brands
filtered_data = data[data['brand'].isin(selected_brands)]

if not filtered_data.empty:
    # Create a matplotlib figure
    fig, ax = plt.subplots(figsize=(12, 6))  # Adjust size as needed

    # Plot the boxplot
    sns.boxplot(x='brand', y='price', data=filtered_data, ax=ax)
    
    # Customize the plot
    ax.set_title("Price Distribution by Brand")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)  # Rotate brand labels for readability

    # Display the plot in Streamlit
    st.pyplot(fig)
else:
    st.write("No data available for the selected brands.")

# ----------------------------------------------------------------------

st.header("Year Distribution by Brand")


# Filter data based on selected brands
filtered_data = data[data['brand'].isin(selected_brands)]

if not filtered_data.empty:
    # Create a matplotlib figure
    fig, ax = plt.subplots(figsize=(12, 6))  # Adjust size as needed

    # Plot the boxplot
    sns.boxplot(x='brand', y='year', data=filtered_data, ax=ax)
    
    # Customize the plot
    ax.set_title("Year Distribution by Brand")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)  # Rotate brand labels for readability

    # Display the plot in Streamlit
    st.pyplot(fig)
else:
    st.write("No data available for the selected brands.")


# --------------------------------------------------------------

st.header("Price Distribution by model")

top_models = data['model'].value_counts().head(5).index.tolist()

# Filter data to avoid clutter if there are too many models
selected_models = st.sidebar.multiselect(
    "Select models to include in the boxplot",
    options=data['model'].unique(),
    default=top_models  # Default to the first 5 models
)

# Filter data based on selected models
filtered_data = data[data['model'].isin(selected_models)]

if not filtered_data.empty:
    # Create a matplotlib figure
    fig, ax = plt.subplots(figsize=(12, 6))  # Adjust size as needed

    # Plot the boxplot
    sns.boxplot(x='model', y='price', data=filtered_data, ax=ax)
    
    # Customize the plot
    ax.set_title("Price Distribution by model")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)  # Rotate model labels for readability

    # Display the plot in Streamlit
    st.pyplot(fig)
else:
    st.write("No data available for the selected models.")

# ----------------------------------------------------------------------

st.header("Year Distribution by model")


# Filter data based on selected models
filtered_data = data[data['model'].isin(selected_models)]

if not filtered_data.empty:
    # Create a matplotlib figure
    fig, ax = plt.subplots(figsize=(12, 6))  # Adjust size as needed

    # Plot the boxplot
    sns.boxplot(x='model', y='year', data=filtered_data, ax=ax)
    
    # Customize the plot
    ax.set_title("Year Distribution by model")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)  # Rotate model labels for readability

    # Display the plot in Streamlit
    st.pyplot(fig)
else:
    st.write("No data available for the selected models.")


# --------------------------------------------------------------
# Provide an option to download the cleaned data
st.header("Export Data")
if st.button("Download Cleaned Data as Excel"):
    excel_data = convert_df_to_excel(data)
    st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name="cleaned_car_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Footer
st.write("Built with ❤️ using Streamlit!")

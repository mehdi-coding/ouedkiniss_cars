import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from utils import load_data_from_db, clean_data

st.title("💰 Price Range Analysis")

# Load & clean
data = load_data_from_db()
data = clean_data(data)

# Sidebar - Price Range Selection
st.sidebar.subheader("Filter by Price Range")
min_price = int(data['price'].min())
max_price = int(data['price'].max())

price_range = st.sidebar.slider(
    "Select price range",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=1
)

# Apply filter
filtered_data = data[
    (data['price'] >= price_range[0]) & 
    (data['price'] <= price_range[1])
]

st.write(f"📊 Data available in selected range: {filtered_data.shape[0]} rows")

# Show summary
st.subheader("Statistical Summary")
st.write(filtered_data.describe().drop(columns=['wilaya']))

# -----------------------------------
# Brand analysis
st.header("Brand Analysis in Price Range")

brand_counts = filtered_data['brand'].value_counts().reset_index()
brand_counts.columns = ['brand', 'count']

brand_avg_price = filtered_data.groupby('brand')['price'].mean().reset_index()
brand_avg_price.columns = ['brand', 'Average Price']

merged_brand = pd.merge(brand_counts, brand_avg_price, on="brand")
st.write(merged_brand)

# Plot - top brands
top_brands = merged_brand.head(10)
fig = px.bar(
    top_brands, 
    x="brand", y="count",
    title="Top 10 Brands in Selected Price Range",
    text="count"
)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# Model analysis
st.header("Model Analysis in Price Range")

model_counts = filtered_data['model'].value_counts().reset_index()
model_counts.columns = ['model', 'count']

model_avg_price = filtered_data.groupby('model')['price'].mean().reset_index()
model_avg_price.columns = ['model', 'Average Price']

merged_model = pd.merge(model_counts, model_avg_price, on="model")
st.write(merged_model)

# Plot - top models
top_models = merged_model.head(10)
fig = px.bar(
    top_models, 
    x="model", y="count",
    title="Top 10 Models in Selected Price Range",
    text="count"
)
st.plotly_chart(fig, use_container_width=True)


# -----------------------------------
# Boxplot for top 5 models in price range
st.header("Price Distribution of Top 5 Models")

# Find top 5 models by count in the filtered data
top_5_models = (
    filtered_data['model']
    .value_counts()
    .head(5)
    .index
    .tolist()
)

# Filter only those models
top_models_data = filtered_data[filtered_data['model'].isin(top_5_models)]

if not top_models_data.empty:
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(x="model", y="price", data=top_models_data, ax=ax)
    
    # Customize
    ax.set_title("Price Distribution of Top 5 Models")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    st.pyplot(fig)
else:
    st.write("⚠️ No data available for the selected price range.")

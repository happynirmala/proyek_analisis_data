import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium

# Load datasets
order_items = pd.read_csv('order_items_dataset.csv')
products = pd.read_csv('products_dataset.csv')
product_category_translation = pd.read_csv('product_category_name_translation.csv')
orders = pd.read_csv('orders_dataset.csv')
sellers = pd.read_csv('sellers_dataset.csv')
customers = pd.read_csv('customers_dataset.csv')
geolocation = pd.read_csv('geolocation_dataset.csv')

# Merge datasets for product revenue analysis
order_items_products = pd.merge(order_items, products, on='product_id', how='left')
order_items_products = pd.merge(order_items_products, product_category_translation, on='product_category_name', how='left')

# Handle missing values
order_items_products['product_category_name_english'] = order_items_products['product_category_name_english'].fillna('Unknown')

# Add revenue column (quantity * price)
order_items_products['revenue'] = order_items_products['price'] * order_items_products['order_item_id']

# Calculate total revenue by product category
category_revenue = order_items_products.groupby('product_category_name_english')['revenue'].sum().reset_index()

# Sort by revenue and select the top 20 categories
top_20_category_stats = category_revenue.sort_values(by='revenue', ascending=False).head(20)

# Streamlit Dashboard Title
st.title('E-Commerce Dashboard')

# Section 1: Top 20 Categories by Revenue
st.header('Top 20 Categories by Revenue')

# Show the top 20 table on the dashboard
st.write("Top 20 Product Categories by Revenue:")
st.dataframe(top_20_category_stats)

# Visualization of the top 20 categories
plt.figure(figsize=(14, 8))
plt.barh(top_20_category_stats['product_category_name_english'], top_20_category_stats['revenue'], color='skyblue')
plt.xlabel('Revenue')
plt.ylabel('Product Category')
plt.title('Top 20 Product Categories by Revenue')
plt.tight_layout()

# Display the bar chart in Streamlit
st.pyplot(plt)

# Section 2: Estimated vs. Actual Delivery Dates (Scatter Plot)
# Prepare data for delivery accuracy analysis
orders_delivery = orders[['order_id', 'order_estimated_delivery_date', 'order_delivered_customer_date']]

# Convert date columns to datetime
orders_delivery['order_estimated_delivery_date'] = pd.to_datetime(orders_delivery['order_estimated_delivery_date'], errors='coerce')
orders_delivery['order_delivered_customer_date'] = pd.to_datetime(orders_delivery['order_delivered_customer_date'], errors='coerce')

# Calculate delivery accuracy in days
orders_delivery['delivery_accuracy'] = (
    orders_delivery['order_estimated_delivery_date'] - orders_delivery['order_delivered_customer_date']
).dt.days

orders_delivery.dropna(subset=['order_estimated_delivery_date', 'order_delivered_customer_date'], inplace=True)

# Section Title for Scatter Plot
st.header('Estimated vs. Actual Delivery Dates')

# Create the scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(
    orders_delivery['order_estimated_delivery_date'],
    orders_delivery['order_delivered_customer_date'],
    c=orders_delivery['delivery_accuracy'],
    cmap='coolwarm',
    alpha=0.6
)

# Add a color bar to interpret the accuracy
plt.colorbar(label='Delivery Accuracy (days)')

# Adding explanatory details (title, labels)
plt.title('Estimated vs. Actual Delivery Dates', fontsize=16)
plt.xlabel('Estimated Delivery Date', fontsize=14)
plt.ylabel('Actual Delivery Date', fontsize=14)

# Display the scatter plot in Streamlit
st.pyplot(plt)

# Section 3: Geospatial Analysis

# Drop duplicates in geolocation data
geolocation = geolocation.drop_duplicates(subset='geolocation_zip_code_prefix')

# Merge sellers and customers with geolocation data based on zip_code_prefix
sellers_geo = pd.merge(sellers, geolocation, how='left', left_on='seller_zip_code_prefix', right_on='geolocation_zip_code_prefix')
customers_geo = pd.merge(customers, geolocation, how='left', left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix')

# Remove rows with NaN values in latitude or longitude
sellers_geo.dropna(subset=['geolocation_lat', 'geolocation_lng'], inplace=True)
customers_geo.dropna(subset=['geolocation_lat', 'geolocation_lng'], inplace=True)

# Create a map centered around the mean of the lat/lon data
m = folium.Map(location=[geolocation['geolocation_lat'].mean(), geolocation['geolocation_lng'].mean()], zoom_start=4)

# Add seller locations to the map
for idx, row in sellers_geo.iterrows():
    folium.Marker(
        location=[row['geolocation_lat'], row['geolocation_lng']],
        popup=row['seller_city'],
        icon=folium.Icon(color='blue', icon='store')
    ).add_to(m)

# Add customer locations to the map
for idx, row in customers_geo.iterrows():
    folium.Marker(
        location=[row['geolocation_lat'], row['geolocation_lng']],
        popup=row['customer_city'],
        icon=folium.Icon(color='green', icon='user')
    ).add_to(m)

# Display the map in Streamlit
st.header('Geospatial Analysis: Sellers and Customers Locations')
st_folium(m, width=700)
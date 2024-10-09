import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

st.title("Dicoding E-Commerce Dashboard")

# Sidebar date range filter
date_range = st.sidebar.date_input(
    "Rentang Waktu",
    value=(pd.to_datetime('2021-01-01'), pd.to_datetime('2021-05-31'))
)

# Load datasets
sellers = pd.read_csv('sellers_dataset.csv')
products = pd.read_csv('products_dataset.csv')
orders_review = pd.read_csv('order_reviews_dataset.csv')
orders = pd.read_csv('orders_dataset.csv')
product_category_translation = pd.read_csv('product_category_name_translation.csv')
order_items = pd.read_csv('order_items_dataset.csv')
order_payments = pd.read_csv('order_payments_dataset.csv')
geolocation = pd.read_csv('geolocation_dataset.csv')
customers = pd.read_csv('customers_dataset.csv')

# 1. Clustered Bar Chart: Total Revenue by Product Category

# Merge datasets for revenue calculation
order_items_products = pd.merge(order_items, products, on='product_id', how='left')
order_items_products = pd.merge(order_items_products, product_category_translation, on='product_category_name', how='left')

# Calculate revenue per product
order_items_products['revenue'] = order_items_products['price']

# Calculate total revenue per category
category_revenue = order_items_products.groupby('product_category_name_english')['revenue'].sum().reset_index()

# Merge revenue and sort by highest revenue
category_stats = category_revenue.sort_values(by='revenue', ascending=False)

# Plot clustered bar chart
st.subheader("Best & Worst Performing Product")

plt.figure(figsize=(10, 6))
bar_width = 0.35
positions = range(len(category_stats.head(20)))

plt.barh(positions, category_stats['revenue'].head(20), height=bar_width, label='Total Revenue', color='lightblue')

plt.xlabel('Total Revenue')
plt.ylabel('Product Category')
plt.yticks(positions, category_stats['product_category_name_english'].head(20))
plt.title('Total Revenue by Product Category (Top 20)')
st.pyplot(plt)

# 2. Scatter Plot: Estimated vs. Actual Delivery Dates

orders_delivery = orders[['order_id', 'order_estimated_delivery_date', 'order_delivered_customer_date']].copy()
orders_delivery['order_estimated_delivery_date'] = pd.to_datetime(orders_delivery['order_estimated_delivery_date'])
orders_delivery['order_delivered_customer_date'] = pd.to_datetime(orders_delivery['order_delivered_customer_date'])

# Calculate delivery accuracy
orders_delivery['delivery_accuracy'] = (orders_delivery['order_estimated_delivery_date'] - orders_delivery['order_delivered_customer_date']).dt.days

# Scatter plot
st.subheader("Estimated vs. Actual Delivery Dates")

plt.figure(figsize=(10, 6))
plt.scatter(
    orders_delivery['order_estimated_delivery_date'],
    orders_delivery['order_delivered_customer_date'],
    c=orders_delivery['delivery_accuracy'],
    cmap='coolwarm',
    alpha=0.6
)
plt.colorbar(label='Delivery Accuracy (days)')
plt.xlabel('Estimated Delivery Date')
plt.ylabel('Actual Delivery Date')
plt.title('Estimated vs. Actual Delivery Dates')
st.pyplot(plt)

# 3. Map: Geospatial Analysis with Folium

st.subheader("Geospatial Analysis")

# Drop duplicates in geolocation data
geolocation = geolocation.drop_duplicates(subset='geolocation_zip_code_prefix')

# Merge geolocation data with sellers and customers
sellers_geo = pd.merge(sellers, geolocation, how='left', left_on='seller_zip_code_prefix', right_on='geolocation_zip_code_prefix')
customers_geo = pd.merge(customers, geolocation, how='left', left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix')

# Create a base map centered around Brazil
m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

# Add HeatMap layer for sellers
sellers_location = sellers_geo[['geolocation_lat', 'geolocation_lng']].dropna()
HeatMap(data=sellers_location, radius=10).add_to(m)

# Display the map
st_folium(m, width=700, height=500)

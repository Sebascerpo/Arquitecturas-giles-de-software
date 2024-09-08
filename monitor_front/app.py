import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Function to fetch data from the endpoint


def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return []


# Fetch data
data = fetch_data("http://monitor:5000/logs")

# Convert data to DataFrame
if data:
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['disposability'] = df['status'].apply(lambda x: 1 if x == 200 else 0)

    # Plot data
    st.title("App Disposability Over Time")

    fig, ax = plt.subplots()
    ax.plot(df['timestamp'], df['disposability'], marker='o', linestyle='-')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Disposability (1 = Available, 0 = Not Available)')
    ax.set_title('Disposability of the App Over Time')

    # Rotate x-axis labels to vertical
    plt.xticks(rotation=90)

    ax.grid(True)
    st.pyplot(fig)

else:
    st.write("No data available to display.")

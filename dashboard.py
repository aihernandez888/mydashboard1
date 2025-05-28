
import streamlit as st
import requests
import time

# Set page config
st.set_page_config(page_title="Claremont Dashboard", layout="wide")

# Custom background with gradient using Streamlit markdown and HTML
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to right, #4facfe, #00f2fe);
        color: white;
    }
    .ticker {
        position: fixed;
        bottom: 0;
        width: 100%;
        overflow: hidden;
        background-color: rgba(0, 0, 0, 0.6);
        color: white;
        font-size: 18px;
        white-space: nowrap;
        animation: scroll-left 20s linear infinite;
    }
    @keyframes scroll-left {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.title("🌤️ Claremont, CA Daily Dashboard")
st.markdown("Updated every minute • Weather • News Headlines")

# Weather block (NWS API)
def get_weather_forecast():
    try:
        # Claremont, CA lat/lon
        points_url = "https://api.weather.gov/points/34.0961,-117.7198"
        points_data = requests.get(points_url).json()
        forecast_url = points_data["properties"]["forecast"]
        forecast_data = requests.get(forecast_url).json()
        current_forecast = forecast_data["properties"]["periods"][0]
        return f"{current_forecast['name']}: {current_forecast['temperature']}°{current_forecast['temperatureUnit']} - {current_forecast['shortForecast']}"
    except Exception as e:
        return f"Error getting weather: {e}"

weather = get_weather_forecast()
st.subheader("☁️ Current Weather")
st.write(weather)

# News ticker (example: using NewsAPI)
def get_news_headlines():
    try:
        api_key = "your_newsapi_key_here"
        url = f"https://newsapi.org/v2/top-headlines?category=science&language=en&apiKey={api_key}"
        response = requests.get(url).json()
        headlines = [article['title'] for article in response['articles'][:5]]
        return " • ".join(headlines)
    except Exception as e:
        return "Could not fetch news headlines."

news_ticker = get_news_headlines()

# Simulate ticker
st.markdown(f"<div class='ticker'>{news_ticker}</div>", unsafe_allow_html=True)

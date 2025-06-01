
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
st.title("🌤️ Alan's Daily Dashboard")
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
import streamlit as st
import time
import feedparser

def fetch_news_headlines():
    feed_url = "https://www.reddit.com/r/news/.rss"
    feed = feedparser.parse(feed_url)
    headlines = [entry.title for entry in feed.entries[:10]]
    return headlines

news_headlines = fetch_news_headlines()
ticker_text = "   |   ".join(news_headlines)
ticker_placeholder = st.empty()

while True:
    for i in range(len(ticker_text)):
        ticker_placeholder.markdown(
            f"<h4 style='color:white; background-color:#111; padding:10px;'>{ticker_text[i:] + '   |   ' + ticker_text[:i]}</h4>", 
            unsafe_allow_html=True)
        time.sleep(0.1)


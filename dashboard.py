
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
import requests
import feedparser

def fetch_news_headlines():
    feed_url = "https://www.reddit.com/r/space/.rss"
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; MyApp/1.0)'}
    response = requests.get(feed_url, headers=headers)
    feed = feedparser.parse(response.content)
    headlines = [entry.title for entry in feed.entries[:10]]  # top 10 headlines
    return headlines

import streamlit as st
import requests
import feedparser
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 60 seconds (60000 ms)
count = st_autorefresh(interval=60000, limit=None, key="ticker_refresh")

def fetch_news_headlines():
    feed_url = "https://www.reddit.com/r/space/.rss"
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; MyApp/1.0)'}
    response = requests.get(feed_url, headers=headers)
    feed = feedparser.parse(response.content)
    headlines = [entry.title for entry in feed.entries[:10]]  # top 10 headlines
    return headlines

headlines = fetch_news_headlines()

if headlines:
    colors = ["#FF6347", "#4CAF50", "#2196F3", "#FFD700"]  # cycle of colors

    colored_headlines = []
    for i, hl in enumerate(headlines):
        color = colors[i % len(colors)]
        colored_headlines.append(f'<span style="color:{color}; margin-right: 30px;">{hl}</span>')

    ticker_text = ''.join(colored_headlines)
    ticker_text = ticker_text + ticker_text  # duplicate for seamless scrolling

    ticker_html = f"""
    <div style="position: fixed; bottom: 0; width: 100%; background: #222; overflow: hidden; white-space: nowrap; box-sizing: border-box; padding: 10px 0; z-index: 1000;">
      <div style="display: inline-block; padding-left: 100%; animation: ticker 45s linear infinite;">
        {ticker_text}
      </div>
    </div>

    <style>
    @keyframes ticker {{
      0% {{ transform: translate3d(0, 0, 0); }}
      100% {{ transform: translate3d(-50%, 0, 0); }}
    }}
    </style>
    """

    st.markdown(ticker_html, unsafe_allow_html=True)

#NASA IMAGE
import streamlit as st
import requests
import random
from datetime import datetime, timedelta
from streamlit_extras import add_vertical_space

# Title
st.set_page_config(layout="wide", page_title="NASA Space Image Viewer")
st.markdown("<h1 style='text-align: center;'>🚀 Random NASA Space Image</h1>", unsafe_allow_html=True)

# NASA API key (demo or your own from api.nasa.gov)
NASA_API_KEY = "DEMO_KEY"  # Replace with your own key for higher limits

# Function to fetch a random APOD image from the last 10 days
def fetch_random_apod():
    # Pick a random date in the past 10 days
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10)]
    random_date = random.choice(dates)

    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={random_date}"
    response = requests.get(url).json()

    return response

# Refresh every 180,000 milliseconds (3 minutes)
st.experimental_rerun = st.experimental_rerun if hasattr(st, "experimental_rerun") else lambda: None
st.experimental_set_query_params(updated=str(datetime.now()))
st_autorefresh = st.experimental_rerun
st_autorefresh()

# Display image
apod = fetch_random_apod()
if apod.get("media_type") == "image":
    st.image(apod["url"], caption=apod.get("title", ""), use_column_width=True)
else:
    st.warning("Today’s APOD is a video or unsupported media type. Refresh for another image.")

# Description
if "explanation" in apod:
    with st.expander("📖 Image Description"):
        st.markdown(apod["explanation"])


else:
    st.write("No headlines found.")

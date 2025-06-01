import streamlit as st
import requests
import feedparser
import random
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# === PAGE CONFIG: MUST BE FIRST COMMAND ===
st.set_page_config(page_title="Claremont Dashboard", layout="wide")

# === CSS STYLING ===
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to right, #4facfe, #00f2fe);
        color: white;
    }
    /* News ticker styling */
    .ticker-container {
        position: fixed;
        bottom: 0;
        width: 100%;
        background: rgba(0, 0, 0, 0.6);
        overflow: hidden;
        white-space: nowrap;
        box-sizing: border-box;
        padding: 10px 0;
        z-index: 1000;
        font-size: 18px;
    }
    .ticker-content {
        display: inline-block;
        padding-left: 100%;
        animation: ticker 45s linear infinite;
    }
    @keyframes ticker {
      0% { transform: translate3d(0, 0, 0); }
      100% { transform: translate3d(-50%, 0, 0); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# === AUTO REFRESH ===
# Refresh every 60 seconds for weather & news ticker
count = st_autorefresh(interval=60000, limit=None, key="refresh_every_minute")

# === HEADER ===
st.title("🌤️ Alan's Daily Dashboard")
st.markdown("Updated every minute • Weather • News Headlines")

# === WEATHER ===
def get_weather_forecast():
    try:
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

# === NEWS TICKER ===
def fetch_news_headlines():
    feed_url = "https://www.reddit.com/r/space/.rss"
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; MyApp/1.0)'}
    response = requests.get(feed_url, headers=headers)
    feed = feedparser.parse(response.content)
    headlines = [entry.title for entry in feed.entries if "imgur.com" not in entry.link][:10]  # filter out some non-news or images links
    return headlines

headlines = fetch_news_headlines()

if headlines:
    colors = ["#FF6347", "#4CAF50", "#2196F3", "#FFD700"]  # cycle of colors

    colored_headlines = []
    for i, hl in enumerate(headlines):
        color = colors[i % len(colors)]
        colored_headlines.append(f'<span style="color:{color}; margin-right: 30px;">{hl}</span>')

    ticker_text = ''.join(colored_headlines)
    ticker_text += ticker_text  # duplicate for seamless looping

    ticker_html = f"""
    <div class="ticker-container">
      <div class="ticker-content">
        {ticker_text}
      </div>
    </div>
    """

    st.markdown(ticker_html, unsafe_allow_html=True)

else:
    st.write("No headlines found.")

# === NASA RANDOM SPACE IMAGE (APOD) ===
# Refresh every 3 minutes (180000 ms)
if count % 3 == 0:
    st.session_state['apod'] = None  # force refresh every 3 mins

NASA_API_KEY = "DEMO_KEY"  # Replace with your NASA API key for higher limits

def fetch_random_apod():
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10)]
    random_date = random.choice(dates)
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={random_date}"
    response = requests.get(url).json()
    return response

if 'apod' not in st.session_state or st.session_state['apod'] is None:
    st.session_state['apod'] = fetch_random_apod()

apod = st.session_state['apod']

st.markdown("<h2 style='text-align:center;'>🚀 Random NASA Space Image</h2>", unsafe_allow_html=True)

if apod.get("media_type") == "image":
    nasa_img_html = f"""
    <div style="
        position: fixed;
        top: 70px;
        right: 20px;
        width: 250px;
        height: auto;
        z-index: 10000;
        border: 3px solid white;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        background-color: #000000cc;
        padding: 5px;
    ">
        <img src="{apod['url']}" alt="{apod.get('title', '')}" style="width: 100%; height: auto; border-radius: 5px;" />
        <div style="color: white; font-size: 12px; text-align: center; margin-top: 4px;">
            {apod.get('title', '')}
        </div>
    </div>
    """
    st.markdown(nasa_img_html, unsafe_allow_html=True)
else:
    st.warning("Today’s APOD is a video or unsupported media type. Refresh for another image.")

if "explanation" in apod:
    with st.expander("📖 Image Description"):
        st.markdown(apod["explanation"])

import streamlit as st
import requests
import feedparser
import random
from datetime import datetime, time
import pytz
from streamlit_autorefresh import st_autorefresh
import yfinance as yf

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

    /* Top right image styling */
    .top-right-image {
        position: fixed;
        top: 75px;
        right: 20px;
        width: 300px;
        z-index: 9999;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# === AUTO REFRESH ===
# Refresh every 60 seconds for weather & news ticker
st_autorefresh(interval=600000, limit=None, key="refresh_every_10min")


# === HEADER ===
st.title("🌤️ Alan's Daily Dashboard")
st.markdown("Updated every minute • Weather • News Headlines")

# === WEATHER FUNCTIONS ===
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

def get_hourly_forecast():
    try:
        points_url = "https://api.weather.gov/points/34.0961,-117.7198"
        points_data = requests.get(points_url).json()
        hourly_url = points_data["properties"]["forecastHourly"]
        hourly_data = requests.get(hourly_url).json()
        periods = hourly_data["properties"]["periods"]

        tz = pytz.timezone("America/Los_Angeles")
        today = datetime.now(tz).date()

        def get_emoji(forecast):
            forecast = forecast.lower()
            if "sunny" in forecast or "clear" in forecast:
                return "☀️"
            elif "cloud" in forecast:
                return "☁️"
            elif "rain" in forecast or "showers" in forecast:
                return "🌧️"
            elif "storm" in forecast or "thunder" in forecast:
                return "⛈️"
            elif "snow" in forecast:
                return "❄️"
            elif "wind" in forecast or "breezy" in forecast:
                return "🌬️"
            else:
                return "🌡️"

        hourly_strings = []
        for period in periods:
            start_time_utc = datetime.fromisoformat(period["startTime"].replace("Z", "+00:00"))
            start_time_local = start_time_utc.astimezone(tz)
            if start_time_local.date() == today and time(8, 0) <= start_time_local.time() <= time(20, 0):
                hour_str = start_time_local.strftime("%-I %p")
                temp = period["temperature"]
                unit = period["temperatureUnit"]
                short_forecast = period["shortForecast"]
                emoji = get_emoji(short_forecast)
                hourly_strings.append(f"{hour_str}: {temp}°{unit} {emoji}")

        return " | ".join(hourly_strings)

    except Exception as e:
        return f"Error getting hourly forecast: {e}"

# === STOCKS FUNCTION ===
def get_stock_ticker_text(symbols):
    stock_texts = []
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="2d")
            if data.empty or len(data) < 2:
                continue
            latest = data.iloc[-1]
            prev = data.iloc[-2]
            price = latest['Close']
            prev_close = prev['Close']
            pct_change = (price - prev_close) / prev_close * 100

            if pct_change > 0:
                emoji = "🔺"
                color = "lightgreen"
            elif pct_change < 0:
                emoji = "🔻"
                color = "#ff7f7f"
            else:
                emoji = "⏺️"
                color = "white"

            pct_change_str = f"{pct_change:+.2f}%"
            stock_html = f'<span style="color: {color}; margin-right: 20px;">{symbol}: ${price:.2f} {emoji} {pct_change_str}</span>'
            stock_texts.append(stock_html)

        except Exception:
            stock_texts.append(f'<span style="color: white; margin-right: 20px;">{symbol}: Error</span>')

    return " ".join(stock_texts)

# === NEWS TICKER FUNCTION ===
def fetch_news_headlines():
    feed_url = "https://www.reddit.com/r/space/.rss"
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; MyApp/1.0)'}
    response = requests.get(feed_url, headers=headers)
    feed = feedparser.parse(response.content)
    headlines = [entry.title for entry in feed.entries if "imgur.com" not in entry.link][:10]
    return headlines

# === DISPLAY WEATHER, STOCKS, NEWS ===
weather = get_weather_forecast()
st.subheader("☁️ Current Weather")
st.write(weather)

hourly_forecast = get_hourly_forecast()

popular_stocks = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
    "NVDA", "META", "BRK-B", "JPM", "V",
    "UNH", "HD", "PG", "MA", "DIS"
]

stock_ticker = get_stock_ticker_text(popular_stocks)
headlines = fetch_news_headlines()

if headlines:
    colors = ["#FF6347", "#4CAF50", "#2196F3", "#FFD700"]
    colored_headlines = []
    for i, hl in enumerate(headlines):
        color = colors[i % len(colors)]
        colored_headlines.append(f'<span style="color:{color}; margin-right: 30px;">{hl}</span>')

    ticker_text = ''.join(colored_headlines)
    ticker_text += ticker_text  # duplicate for smooth ticker

    ticker_text = (
        f"<b>Hourly Weather:</b> {hourly_forecast} | "
        f"<b>Stocks:</b> {stock_ticker} | "
        + ticker_text
    )

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

# === NASA / r/spaceporn RANDOM IMAGE TOP RIGHT ===
#st.title("🪐 Your Daily Space View")

#headers = {"User-agent": "Mozilla/5.0"}
#url = "https://www.reddit.com/r/spaceporn/top/.json?t=week&limit=50"

#try:
#    res = requests.get(url, headers=headers, timeout=10)
#    data = res.json()

 #   image_posts = [
 #       post["data"] for post in data["data"]["children"]
 #       if post["data"].get("post_hint") == "image"
 #   ]

 #   if image_posts:
  #      selected_post = random.choice(image_posts)
  #      img_url = selected_post["url"]
  #      title = selected_post["title"]

   #     st.markdown(f"""
   #         <img src="{img_url}" class="top-right-image" title="{title}">
   #     """, unsafe_allow_html=True)
   # else:
  #      st.error("No image posts found. Try refreshing the page.")

#except Exception:
  #  st.error("Error fetching image. Please try again later.")

# === RANDOM RADIO PLAYER ===
st.title("🎧 Random Radio Player")

radio_stations = [
    {"name": "NPR News", "url": "https://npr-ice.streamguys1.com/live.mp3"},
    {"name": "PBS Radio (WNYC)", "url": "https://fm939.wnyc.org/wnycfm"},
    {"name": "Claremont College Radio (88.7 FM)", "url": "https://streaming.radionomy.com/KSPC"},
]

selected_station = random.choice(radio_stations)

st.write(f"▶️ Now playing: **{selected_station['name']}**")
st.audio(selected_station["url"], format="audio/mp3", start_time=0)

# === CHATGPT LINK WITH ROBOT EMOJI ===
st.markdown(
    """
    <a href="https://chat.openai.com" target="_blank" style="font-size: 40px; text-decoration:none;">
        🤖
    </a>
    """,
    unsafe_allow_html=True
)

# Date and Time

import streamlit as st
import streamlit.components.v1 as components

components.html(
    """
    <div id="clock" style="
        font-family: 'Courier New', monospace;
        font-size: 7vw;
        color: red;
        font-weight: bold;
        text-align: center;
        letter-spacing: 2px;
        padding: 20px 0 40px 0;
    ">
    </div>

    <script>
    function updateClock() {
        const now = new Date();
        const options = {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
            second: 'numeric',
            hour12: true
        };
        document.getElementById('clock').textContent = now.toLocaleString('en-US', options);
    }
    setInterval(updateClock, 1000);
    updateClock();
    </script>
    """,
    height=150,  // Increase height to fit on mobile
    scrolling=False,
)


# Bob Ross

import streamlit as st
import random

# List of Bob Ross video IDs
bob_ross_videos = [
    "oh5p5f5_-7A",
    "1AIeDl5sHVI",
    "Lel6x5V_T6g",
    "jajcg59aKZw",
    "TdphtMWjies",
    "Z2F2TcEM4v0",
    "YLO7tCdBVrA",
    "9cL2OHU85no",
    "hYw2I2YJz2k",
    "iVgNe-8a_RI"
]

# Pick a random video
video_id = random.choice(bob_ross_videos)

# Embed iframe using markdown
video_html = f"""
<iframe width="320" height="180"
    src="https://www.youtube.com/embed/{video_id}?autoplay=1&rel=0"
    title="Random Bob Ross Episode"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen>
</iframe>
"""

st.markdown(video_html, unsafe_allow_html=True)

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
    <link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">

    <style>
        body {
            margin: 0;
            padding: 0;
        }

        #clock-container {
            font-family: 'VT323', monospace;
            font-size: 60px;
            color: red;
            background-color: #111;
            text-align: center;
            padding: 30px 10px;
            animation: pulse 2s infinite;
            letter-spacing: 2px;
        }

        @keyframes pulse {
            0% { text-shadow: 0 0 5px red, 0 0 10px red, 0 0 15px red; }
            50% { text-shadow: 0 0 10px red, 0 0 20px red, 0 0 30px red; }
            100% { text-shadow: 0 0 5px red, 0 0 10px red, 0 0 15px red; }
        }

        .colon {
            animation: blink 1.5s infinite;
        }

        .ampm {
            animation: blink 1.5s infinite;
            
        }

        @keyframes blink {
            0%, 49% { opacity: 1; }
            50%, 100% { opacity: 0; }
        }
    </style>

    <div id="clock-container"></div>

    <script>
        function formatTime(date) {
            let hours = date.getHours();
            const minutes = date.getMinutes();
            const seconds = date.getSeconds();
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12; // the hour '0' should be '12'

            const dayOptions = { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' };
            const dayString = date.toLocaleDateString('en-US', dayOptions);

            return `${dayString} <br> ${hours}<span class="colon">:</span>${String(minutes).padStart(2, '0')}<span class="colon">:</span>${String(seconds).padStart(2, '0')} <span class="ampm">${ampm}</span>`;
        }

        function updateClock() {
            const now = new Date();
            document.getElementById('clock-container').innerHTML = formatTime(now);
        }

        setInterval(updateClock, 1000);
        updateClock();
    </script>
    """,
    height=300,
    scrolling=False,
)




# Bob Ross

import streamlit as st
import random

# List of Bob Ross video IDs
bob_ross_videos = [
    #Season 30
    "vGsW_6BCukU",
    "Xzv3iiWi1Wo",
    "BSjee-ond7w",
    "LEz4UVL7POE",
    "enutOy-nsZk",
    "CY6sGFs209E",
    "jq8bIbpW7DQ",
    "eTEKGOi6SVg",
    "fz0YjqtHW84"
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

#trex thing

import streamlit as st
import streamlit.components.v1 as components

components.html(
    f"""
    <div id="overlay"></div>
    <div id="dino" onclick="triggerDinoEffect()" style="font-size: 50px; cursor: pointer; text-align: center;">🦖</div>
    
    <audio id="roar" src="https://www.soundjay.com/animal/dinosaur-roar-01.mp3"></audio>
    <audio id="stomp" src="https://www.soundjay.com/mechanical/sledge-hammer-1.mp3"></audio>
    
    <style>
        #overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.6);
            z-index: 999;
            display: none;
        }}
        .shake {{
            animation: shake 0.5s;
            animation-iteration-count: 3;
        }}
        @keyframes shake {{
            0% {{ transform: translate(0px, 0px); }}
            25% {{ transform: translate(5px, -5px); }}
            50% {{ transform: translate(-5px, 5px); }}
            75% {{ transform: translate(5px, 5px); }}
            100% {{ transform: translate(0px, 0px); }}
        }}
    </style>

    <script>
        function triggerDinoEffect() {{
            const roar = document.getElementById("roar");
            const stomp = document.getElementById("stomp");
            const overlay = document.getElementById("overlay");

            overlay.style.display = "block";
            document.body.classList.add("shake");

            roar.play();

            setTimeout(() => {{
                stomp.play();
            }}, 1000);

            setTimeout(() => {{
                stomp.play();
            }}, 1800);

            setTimeout(() => {{
                document.body.classList.remove("shake");
                overlay.style.display = "none";
            }}, 2500);
        }}
    </script>
    """,
    height=200,
    scrolling=False,
)


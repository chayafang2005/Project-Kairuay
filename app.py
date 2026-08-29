import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import feedparser
from datetime import datetime

st.set_page_config(page_title="Project Kairuay", layout="wide")

if 'search_ticker' not in st.session_state:
    st.session_state.search_ticker = "AAPL"

st.title("📈 Project Kairuay: คลังข้อมูลและกราฟหุ้นสหรัฐฯ")
st.write("พิมพ์ค้นหาชื่อหุ้นหรือเลือกจากรายการแนะนำด้านล่างเพื่อดูข้อมูล กราฟแท่งเทียน และข่าวสารแบบครบจบในหน้าเดียวครับ")

# ==========================================
# ส่วนที่ 1: ช่องค้นหาแบบพิมพ์แล้วขึ้นแนะนำอัตโนมัติ (Search & Auto-suggest)
# ==========================================
# รายชื่อหุ้นตัวอย่างขนาดใหญ่ในตลาดสหรัฐฯ ที่จะให้ระบบช่วยแนะนำเวลาพิมพ์
all_us_stocks = [
    "AAPL - Apple Inc.", "MSFT - Microsoft Corporation", "GOOGL - Alphabet Inc. (Google)", 
    "AMZN - Amazon.com Inc.", "NVDA - NVIDIA Corporation", "TSLA - Tesla Inc.", 
    "META - Meta Platforms Inc.", "NFLX - Netflix Inc.", "AMD - Advanced Micro Devices", 
    "INTC - Intel Corporation", "MU - Micron Technology", "PLTR - Palantir Technologies",
    "RKLB - Rocket Lab USA", "ONDS - Ondas Holdings", "COIN - Coinbase Global",
    "JPM - JPMorgan Chase & Co.", "V - Visa Inc.", "JNJ - Johnson & Johnson",
    "WMT - Walmart Inc.", "DIS - The Walt Disney Company", "BAC - Bank of America",
    "XOM - Exxon Mobil Corp.", "PFE - Pfizer Inc.", "PYPL - PayPal Holdings"
]

# ใช้ st.selectbox ที่ผู้ใช้สามารถพิมพ์กรองตัวอักษรเพื่อหาหุ้นได้เหมือนช่องค้นหาอัจฉริยะ
selected_stock_item = st.selectbox(
    "🔍 พิมพ์ชื่อย่อหรือชื่อบริษัทเพื่อค้นหา (ระบบจะแนะนำรายชื่อให้อัตโนมัติ):", 
    all_us_stocks,
    index=0
)

# ดึงเฉพาะรหัส Ticker ด้านหน้าสุดมาใช้งาน (เช่น "AAPL" จาก "AAPL - Apple Inc.")
extracted_ticker = selected_stock_item.split(" - ")[0].strip()
if extracted_ticker != st.session_state.search_ticker:
    st.session_state.search_ticker = extracted_ticker

st.divider()

ticker_symbol = st.session_state.search_ticker
ticker_data = yf.Ticker(ticker_symbol)
info = ticker_data.info

company_name = info.get('longName') or ticker_symbol

st.markdown(f"## 🏢 {company_name} ({ticker_symbol})")

# ==========================================
# ส่วนที่ 2: แสดงข้อมูลบริษัทและกราฟ (แบ่ง 2 คอลัมน์)
# ==========================================
main_col, info_col = st.columns([2, 1])

with info_col:
    st.markdown("### 📊 ข้อมูลสำคัญของหุ้น")
    sector = info.get('sector', 'ไม่ระบุ')
    industry = info.get('industry', 'ไม่ระบุ')
    market_cap = info.get('marketCap')
    pe_ratio = info.get('trailingPE')
    high_52 = info.get('fiftyTwoWeekHigh')
    low_52 = info.get('fiftyTwoWeekLow')
    summary = info.get('longBusinessSummary', 'ไม่มีข้อมูลคำอธิบายบริษัทในขณะนี้')
    
    st.markdown(f"**กลุ่มธุรกิจ (Sector):** {sector}")
    st.markdown(f"**อุตสาหกรรม:** {industry}")
    
    if market_cap:
        if market_cap >= 1e9:
            st.markdown(f"**มูลค่าตลาด:** {market_cap / 1e9:,.2f}B USD")
        else:
            st.markdown(f"**มูลค่าตลาด:** {market_cap:,.2f} USD")
            
    if pe_ratio:
        st.markdown(f"**P/E Ratio:** {pe_ratio:,.2f}")
    else:
        st.markdown(f"**P/E Ratio:** N/A")
        
    if high_52 and low_52:
        st.markdown(f"**52-Week High/Low:** {low_52:,.2f} - {high_52:,.2f}")
        
    st.markdown("---")
    st.markdown("**📖 ลักษณะธุรกิจ:**")
    if len(summary) > 450:
        summary_short = summary[:450] + "..."
    else:
        summary_short = summary
    st.markdown(f"<p style='color: #d0d0d0; font-size: 13px; line-height: 1.5;'>{summary_short}</p>", unsafe_allow_html=True)

with main_col:
    period_options = {"1 วัน": "1d", "5 วัน": "5d", "1 เดือน": "1mo", "3 เดือน": "3mo", "6 เดือน": "6mo", "1 ปี": "1y", "5 ปี": "5y"}
    selected_period = st.radio("เลือกระยะเวลา", list(period_options.keys()), horizontal=True, key="period_radio")
    period_value = period_options[selected_period]

    interval_value = "1d"
    if period_value == "1d":
        interval_value = "5m" 
    elif period_value == "5d":
        interval_value = "1h"

    history = ticker_data.history(period=period_value, interval=interval_value)
    current_price = info.get('currentPrice') or info.get('regularMarketPrice')

    if not current_price and not history.empty:
        current_price = history['Close'].iloc[-1]

    if not history.empty and current_price:
        past_price = history['Close'].iloc[0]
        price_change = current_price - past_price
        percent_change = (price_change / past_price) * 100
        
        price_str = f"{current_price:,.2f}"
        
        post_market = info.get('postMarketPrice')
        if post_market:
            post_change = post_market - current_price
            post_percent = (post_change / current_price) * 100
            post_color = "#00C805" if post_change >= 0 else "#FF3333"
            post_sign = "+" if post_change >= 0 else ""
            price_str += f' <span style="font-size:15px; color:gray;">(หลังปิดตลาด: {post_market:,.2f} <span style="color:{post_color};">{post_sign}{post_change:,.2f} [{post_sign}{post_percent:.2f}%]</span>)</span>'

        delta_sign = "+" if price_change >= 0 else ""
        delta_str = f"{delta_sign}{price_change:,.2f} ({delta_sign}{percent_change:.2f}%)"
        
        st.metric(label=f"ราคาปัจจุบันเทียบกับหุ้น {selected_period}ที่แล้ว", value=None, delta=delta_str)
        st.markdown(f"### {price_str}", unsafe_allow_html=True)

    if not history.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=history.index,
            open=history['Open'],
            high=history['High'],
            low=history['Low'],
            close=history['Close'],
            name='ราคา',
            increasing_line_color='#00C805',
            decreasing_line_color='#FF3333'
        )])
        
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=400,
            yaxis=dict(side='right', showgrid=False),
            xaxis=dict(showgrid=False, showspikes=True, spikemode='across', spikesnap='cursor', spikecolor="gray", spikethickness=1),
            hovermode="x",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("ไม่พบข้อมูลกราฟหรือสัญลักษณ์หุ้นนี้")

# ==========================================
# ส่วนที่ 3: ข่าวสารและสรุปบทความ
# ==========================================
st.divider()
st.write(f"### 📰 LATEST NEWS & SUMMARY ({ticker_symbol})")

rss_url = f"https://finance.yahoo.com/rss/headline?s={ticker_symbol}"
feed = feedparser.parse(rss_url)

if feed.entries:
    for entry in feed.entries[:6]:
        title = entry.get('title', 'ไม่มีหัวข้อข่าว')
        link = entry.get('link', '#')
        summary = entry.get('summary', 'คลิกที่หัวข้อเพื่ออ่านเนื้อหาฉบับเต็ม')
        
        publisher = "Yahoo Finance"
        if hasattr(entry, 'source') and 'title' in entry.source:
            publisher = entry.source.title
            
        time_str = ""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                time_str = datetime(*entry.published_parsed[:6]).strftime('%d %b %Y, %H:%M')
            except:
                pass

        st.markdown(f"**{publisher}** • {time_str}")
        st.markdown(f"[{title}]({link})")
        st.markdown(f"<p style='color: #b0b0b0; font-size: 13px; margin-top: -5px;'>{summary}</p>", unsafe_allow_html=True)
        st.write("---")
else:
    st.warning("ไม่พบข้อมูลข่าวสารสำหรับหุ้นตัวนี้ในขณะนี้")

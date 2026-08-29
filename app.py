import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import feedparser
from datetime import datetime
from deep_translator import GoogleTranslator

st.title("📈 คลังข้อมูลหุ้น Project Kairuay")

# ช่องพิมพ์ชื่อหุ้น
ticker_symbol = st.text_input("พิมพ์สัญลักษณ์หุ้น (เช่น AAPL, TSLA, ONDS, RKLB)", "RKLB")
ticker_data = yf.Ticker(ticker_symbol)

# ==========================================
# ส่วนที่ 1: ตั้งค่ารูปแบบและช่วงเวลา
# ==========================================
col1, _ = st.columns(2)
with col1:
    graph_type = st.radio("รูปแบบกราฟ", ["กราฟพื้นที่ (เหมือนแอป)", "กราฟแท่งเทียน (เหมือนเว็บ)"], horizontal=True)

period_options = {"1 วัน": "1d", "5 วัน": "5d", "1 เดือน": "1mo", "3 เดือน": "3mo", "6 เดือน": "6mo", "1 ปี": "1y", "5 ปี": "5y"}
selected_period = st.radio("เลือกระยะเวลา", list(period_options.keys()), horizontal=True)
period_value = period_options[selected_period]

interval_value = "1d"
if period_value == "1d":
    interval_value = "5m" 
elif period_value == "5d":
    interval_value = "1h"

history = ticker_data.history(period=period_value, interval=interval_value)
info = ticker_data.info
current_price = info.get('currentPrice') or info.get('regularMarketPrice')

if not current_price and not history.empty:
    current_price = history['Close'].iloc[-1]

# ==========================================
# ส่วนที่ 2: แสดงราคาปัจจุบันและราคาหลังปิดตลาด
# ==========================================
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
        price_str += f' <span style="font-size:16px; color:gray;">(หลังปิดตลาด: {post_market:,.2f} <span style="color:{post_color};">{post_sign}{post_change:,.2f} [{post_sign}{post_percent:.2f}%]</span>)</span>'

    delta_sign = "+" if price_change >= 0 else ""
    delta_str = f"{delta_sign}{price_change:,.2f} ({delta_sign}{percent_change:.2f}%)"
    
    st.metric(label=f"ราคาปัจจุบันเทียบกับ {selected_period}ที่แล้ว", value=None, delta=delta_str)
    st.markdown(f"### {price_str}", unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 3: วาดกราฟ
# ==========================================
if not history.empty:
    first_price = history['Close'].iloc[0]
    fig = go.Figure()
    
    if "พื้นที่" in graph_type:
        if current_price >= first_price:
            line_color = '#00C805' 
            fill_color = 'rgba(0, 200, 5, 0.1)'
        else:
            line_color = '#FF3333'
            fill_color = 'rgba(255, 51, 51, 0.1)'

        history['Pct_Change_Str'] = (((history['Close'] - first_price) / first_price) * 100).apply(lambda x: f"{x:+.2f}%")

        fig.add_trace(go.Scatter(
            x=history.index, 
            y=history['Close'], 
            customdata=history['Pct_Change_Str'],
            mode='lines', 
            name='ราคา',
            line=dict(color=line_color, width=2),
            fill='tozeroy',
            fillcolor=fill_color,
            hovertemplate="<span style='font-size:26px; font-weight:bold;'>%{y:,.2f}</span><br>" +
                          "<span style='font-size:14px; color:gray;'>%{x|%d %b %H:%M}</span><br>" +
                          "<span style='font-size:18px;'>เปลี่ยนแปลง: <b>%{customdata}</b></span><extra></extra>"
        ))
    else:
        fig.add_trace(go.Candlestick(
            x=history.index,
            open=history['Open'],
            high=history['High'],
            low=history['Low'],
            close=history['Close'],
            name='ราคา',
            increasing_line_color='#00C805',
            decreasing_line_color='#FF3333'
        ))
    
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
    st.warning("ไม่พบข้อมูลกราฟของหุ้นนี้")

st.divider()

# ==========================================
# ส่วนที่ 4: ข่าวสาร (แปลเฉพาะหัวข้อ ป้องกัน Server Error)
# ==========================================
st.write("### 📰 LATEST NEWS (สรุปหัวข้อภาษาไทย)")

rss_url = f"https://finance.yahoo.com/rss/headline?s={ticker_symbol}"
feed = feedparser.parse(rss_url)

if feed.entries:
    translator = GoogleTranslator(source='auto', target='th')
    
    for entry in feed.entries[:5]:
        title = entry.get('title', 'ไม่มีหัวข้อข่าว')
        link = entry.get('link', '#')
        
        publisher = "Yahoo Finance"
        if hasattr(entry, 'source') and 'title' in entry.source:
            publisher = entry.source.title
            
        time_str = ""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                time_str = datetime(*entry.published_parsed[:6]).strftime('%d %b %Y, %H:%M')
            except:
                pass

        # แปลเฉพาะหัวข้อข่าวเพื่อป้องกัน Error 500
        try:
            th_title = translator.translate(title)
        except:
            th_title = title

        st.markdown(f"**{publisher}** • {time_str}")
        st.markdown(f"[{th_title}]({link})")
        st.markdown(f"<p style='color: #b0b0b0; font-size: 13px;'>คลิกที่หัวข้อเพื่ออ่านรายละเอียดฉบับเต็มจากแหล่งข่าว</p>", unsafe_allow_html=True)
        st.write("---")
else:
    st.warning("ไม่พบข้อมูลข่าวสารสำหรับหุ้นตัวนี้ในขณะนี้")

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import time
from datetime import datetime

st.title("📈 คลังข้อมูลหุ้น Project Kairuay")

# ช่องพิมพ์ชื่อหุ้น
ticker_symbol = st.text_input("พิมพ์สัญลักษณ์หุ้น (เช่น AAPL, TSLA, ONDS)", "ONDS")
ticker_data = yf.Ticker(ticker_symbol)

# ==========================================
# ส่วนที่ 1: ตั้งค่ารูปแบบและช่วงเวลา
# ==========================================
col1, col2 = st.columns(2)
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
# ส่วนที่ 2: แสดงราคาปัจจุบัน
# ==========================================
if not history.empty and current_price:
    past_price = history['Close'].iloc[0]
    price_change = current_price - past_price
    percent_change = (price_change / past_price) * 100
    
    price_str = f"{current_price:,.2f}"
    delta_str = f"{price_change:+,.2f} ({percent_change:+,.2f}%)"
    
    post_market = info.get('postMarketPrice')
    if post_market:
         price_str += f" (หลังปิดตลาด: {post_market:,.2f})"
         
    st.metric(label=f"ราคาปัจจุบันเทียบกับ {selected_period}ที่แล้ว", value=price_str, delta=delta_str)

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
# ส่วนที่ 4: ข่าวสารย้อนหลัง 1 เดือน (พร้อมแสดงเวลา)
# ==========================================
st.write("**📰 ข่าวสารล่าสุด (เฉพาะ 1 เดือนที่ผ่านมา)**")
news = ticker_data.news

if news:
    # คำนวณเวลา 1 เดือนที่แล้ว (ประมาณ 30 วัน)
    current_time = int(time.time())
    one_month_ago = current_time - (30 * 24 * 60 * 60)
    
    # กรองเฉพาะข่าวที่ใหม่กว่า 1 เดือน
    recent_news = [item for item in news if item.get('providerPublishTime', 0) >= one_month_ago]
    
    if recent_news:
        for item in recent_news[:10]: # แสดงผลสูงสุด 10 ข่าว
            title = item.get('title', f'อ่านข่าวอัปเดตล่าสุดของ {ticker_symbol}')
            link = item.get('link', f'https://finance.yahoo.com/quote/{ticker_symbol}')
            
            # แปลงเวลาเป็น วันที่ และ เวลา (HH:MM)
            pub_time = item.get('providerPublishTime')
            date_str = ""
            if pub_time:
                formatted_time = datetime.fromtimestamp(pub_time).strftime('%d %b %Y, %H:%M')
                date_str = f" *(เมื่อ {formatted_time})*"
                
            st.write(f"- [{title}]({link}){date_str}")
    else:
        st.write("ไม่พบข่าวสารในรอบ 1 เดือนที่ผ่านมา")
else:
    st.write("ไม่พบข่าวสารในขณะนี้")

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

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
         
    st.metric(label=f"ราคาปัจจุบันเทียบกับหลัก {selected_period}ที่แล้ว", value=price_str, delta=delta_str)

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
# ส่วนที่ 4: ข่าวสารสไตล์การ์ด (รองรับโครงสร้างใหม่)
# ==========================================
st.write("### 📰 LATEST NEWS")
news = ticker_data.news

if news:
    for item in news[:6]:
        # รองรับการดึงหัวข้อข่าวจากหลายคีย์ที่ Yahoo อาจจะใช้
        title = item.get('title') or item.get('content') or item.get('headline') or 'อัปเดตข่าวสารการลงทุน'
        
        # จัดการกรณีลิงก์ข่าวอยู่ในรูปแบบ nested dictionary
        link = "#"
        raw_link = item.get('link')
        if isinstance(raw_link, dict):
            link = raw_link.get('url', '#')
        elif isinstance(raw_link, str):
            link = raw_link
            
        publisher = item.get('publisher', 'Yahoo Finance')
        
        # ดึงเวลาข่าว
        pub_time = item.get('providerPublishTime')
        time_str = ""
        if pub_time:
            try:
                time_str = datetime.fromtimestamp(pub_time).strftime('%d %b %Y, %H:%M')
            except:
                pass
            
        # ดึงรูปภาพประกอบข่าว
        img_url = ""
        try:
            thumbnails = item.get('thumbnail', {}).get('resolutions', [])
            if thumbnails:
                img_url = thumbnails[0].get('url', '')
        except:
            pass

        col_news1, col_news2 = st.columns([3, 1])
        
        with col_news1:
            st.markdown(f"**{publisher}** • {time_str}")
            st.markdown(f"[{title}]({link})")
            
        with col_news2:
            if img_url:
                st.image(img_url, use_container_width=True)
                
        st.write("---")
else:
    st.warning("ไม่พบข้อมูลข่าวสารในขณะนี้")

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.title("📈 คลังข้อมูลหุ้น Project Kairuay")

# สร้างช่องให้พิมพ์ชื่อหุ้น
ticker_symbol = st.text_input("พิมพ์สัญลักษณ์หุ้น (เช่น AAPL, TSLA, ONDS)", "ONDS")
ticker_data = yf.Ticker(ticker_symbol)

# ==========================================
# ส่วนที่ 1: ดึงข้อมูลและปุ่มเลือกช่วงเวลา
# ==========================================
period_options = {"1 วัน": "1d", "5 วัน": "5d", "1 เดือน": "1mo", "3 เดือน": "3mo", "6 เดือน": "6mo", "1 ปี": "1y", "5 ปี": "5y"}
selected_period = st.radio("เลือกระยะเวลาของกราฟ", list(period_options.keys()), horizontal=True)
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
# ส่วนที่ 2: แสดงราคาปัจจุบันตัวใหญ่
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
# ส่วนที่ 3: กราฟสไตล์ Yahoo Finance App
# ==========================================
if not history.empty:
    first_price = history['Close'].iloc[0]
    
    # ตั้งเงื่อนไขสี: ถ้าราคาปัจจุบันน้อยกว่าจุดเริ่มต้นให้เป็นสีแดง ถ้ามากกว่าให้เป็นสีเขียว
    if current_price >= first_price:
        line_color = '#00C805' 
        fill_color = 'rgba(0, 200, 5, 0.1)'
    else:
        line_color = '#FF3333'
        fill_color = 'rgba(255, 51, 51, 0.1)'

    # คำนวณเปอร์เซ็นต์การเปลี่ยนแปลงของทุกๆ จุดเพื่อนำไปแสดงในกล่องตอนเอาเมาส์ชี้
    history['Pct_Change'] = ((history['Close'] - first_price) / first_price) * 100

    fig = go.Figure(data=[go.Scatter(
        x=history.index, 
        y=history['Close'], 
        customdata=history['Pct_Change'],
        mode='lines', 
        name='ราคา',
        line=dict(color=line_color, width=2),
        fill='tozeroy', # ระบายสีใต้กราฟ
        fillcolor=fill_color,
        # ปรับแต่งกล่องข้อความตอนลากเมาส์ (ตัวเลขใหญ่)
        hovertemplate="<span style='font-size:24px; font-weight:bold;'>%{y:,.2f}</span><br>" +
                      "<span style='color:gray;'>%{x|%d %b %H:%M}</span><br>" +
                      "เปลี่ยนแปลง: <b>%{customdata:+.2f}%</b><extra></extra>"
    )])
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=400,
        yaxis=dict(side='right', showgrid=False), # ย้ายราคาไปฝั่งขวา
        xaxis=dict(
            showgrid=False,
            showspikes=True, # สร้างเส้น Crosshair แนวตั้ง
            spikemode='across',
            spikesnap='cursor',
            spikecolor="gray",
            spikethickness=1,
        ),
        hovermode="x", # ให้กล่องข้อความลอยตามจุดตัด X
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("ไม่พบข้อมูลกราฟของหุ้นนี้")

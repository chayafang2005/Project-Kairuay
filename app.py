import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# ตั้งชื่อหน้าเว็บ
st.title("📈 คลังข้อมูลหุ้น Project Kairuay")

# สร้างช่องให้พิมพ์ชื่อหุ้น
ticker_symbol = st.text_input("พิมพ์สัญลักษณ์หุ้น (เช่น AAPL, TSLA, PTT.BK สำหรับหุ้นไทย)", "AAPL")

# ใช้คำสั่งดึงข้อมูลจาก Yahoo Finance
ticker_data = yf.Ticker(ticker_symbol)

# เพิ่มปุ่มเลือกช่วงเวลาแบบ Yahoo Finance
period_options = {"1 เดือน": "1mo", "3 เดือน": "3mo", "6 เดือน": "6mo", "1 ปี": "1y", "5 ปี": "5y"}
selected_period = st.radio("เลือกระยะเวลาของกราฟ", list(period_options.keys()), horizontal=True)
period_value = period_options[selected_period]

# ส่วนที่ 1: แสดงราคาและสร้างกราฟย้อนหลัง
st.write(f"**กราฟราคาเส้น (Line Chart) ย้อนหลัง {selected_period}**")
history = ticker_data.history(period=period_value)

if not history.empty:
    # สร้างกราฟเส้น (Line Chart) แบบโต้ตอบได้
    fig = go.Figure(data=[go.Scatter(
        x=history.index, 
        y=history['Close'], 
        mode='lines', 
        name='ราคาปิด (Close)',
        line=dict(color='#0068C9', width=2) # สีน้ำเงินสไตล์กราฟหุ้น
    )])
    
    # ปรับแต่งหน้าตากราฟ
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        height=450,
        yaxis_title="ราคา",
        xaxis_title="วันที่",
        hovermode="x unified" # แสดงเส้นประและกล่องข้อความโชว์ราคาเวลาเอาเมาส์ชี้
    )
    
    # แสดงกราฟบนหน้าเว็บ
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("ไม่พบข้อมูลราคาของหุ้นนี้")

# ส่วนที่ 2: ดึงข่าวสารล่าสุดจาก Yahoo Finance
st.write("**📰 ข่าวสารล่าสุด**")
news = ticker_data.news

if news:
    # ใช้ .get() เพื่อป้องกัน Error
    for item in news[:5]:
        title = item.get('title', f'อ่านข่าวอัปเดตล่าสุดของ {ticker_symbol}')
        link = item.get('link', f'https://finance.yahoo.com/quote/{ticker_symbol}')
        st.write(f"- [{title}]({link})")
else:
    st.write("ไม่พบข่าวสารในขณะนี้")

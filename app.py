import streamlit as st
import yfinance as yf

# ตั้งชื่อหน้าเว็บ
st.title("📈 คลังข้อมูลหุ้น Project Kairuay")

# สร้างช่องให้พิมพ์ชื่อหุ้น
ticker_symbol = st.text_input("พิมพ์สัญลักษณ์หุ้น (เช่น AAPL, TSLA, PTT.BK สำหรับหุ้นไทย)", "AAPL")

# ใช้คำสั่งดึงข้อมูลจาก Yahoo Finance
ticker_data = yf.Ticker(ticker_symbol)

# ส่วนที่ 1: แสดงราคาและสร้างกราฟย้อนหลัง
st.write("**กราฟราคาย้อนหลัง 1 เดือน**")
history = ticker_data.history(period="1mo")

if not history.empty:
    st.line_chart(history['Close'])
else:
    st.warning("ไม่พบข้อมูลราคาของหุ้นนี้")

# ส่วนที่ 2: ดึงข่าวสารล่าสุดจาก Yahoo Finance
st.write("**📰 ข่าวสารล่าสุด**")
news = ticker_data.news

if news:
    # ใช้ .get() เพื่อป้องกัน Error กรณี Yahoo เปลี่ยนโครงสร้างข้อมูล
    for item in news[:5]:
        title = item.get('title', f'อ่านข่าวอัปเดตล่าสุดของ {ticker_symbol}')
        link = item.get('link', f'https://finance.yahoo.com/quote/{ticker_symbol}')
        st.write(f"- [{title}]({link})")
else:
    st.write("ไม่พบข่าวสารในขณะนี้")

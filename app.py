import streamlit as st
import yfinance as yf

# ตั้งชื่อหน้าเว็บ
st.title("📈 คลังข้อมูลหุ้น Project Kairuay")

# สร้างช่องให้พิมพ์ชื่อหุ้น (ค่าเริ่มต้นคือ AAPL)
ticker_symbol = st.text_input("พิมพ์สัญลักษณ์หุ้น (เช่น AAPL, TSLA, PTT.BK สำหรับหุ้นไทย)", "AAPL")

# ใช้คำสั่งดึงข้อมูลจาก Yahoo Finance
ticker_data = yf.Ticker(ticker_symbol)

# ส่วนที่ 1: แสดงราคาและสร้างกราฟย้อนหลัง
st.write("**กราฟราคาย้อนหลัง 1 เดือน**")
history = ticker_data.history(period="1mo") # สามารถเปลี่ยน 1mo เป็น 1y (1 ปี) หรือ 5d (5 วัน) ได้

if not history.empty:
    # นำข้อมูลราคาปิด (Close) มาวาดกราฟเส้น
    st.line_chart(history['Close'])
else:
    st.warning("ไม่พบข้อมูลราคาของหุ้นนี้")

# ส่วนที่ 2: ดึงข่าวสารล่าสุดจาก Yahoo Finance
st.write("**📰 ข่าวสารล่าสุด**")
news = ticker_data.news

if news:
    # วนลูปแสดงพาดหัวข่าว 5 อันดับแรก พร้อมฝังลิงก์ให้กดอ่านต่อ
    for item in news[:5]:
        st.write(f"- [{item['title']}]({item['link']})")
else:
    st.write("ไม่พบข่าวสารในขณะนี้")

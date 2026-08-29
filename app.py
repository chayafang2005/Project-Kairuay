import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# ตั้งชื่อหน้าเว็บ
st.title("📈 คลังข้อมูลหุ้น Project Kairuay")

# สร้างช่องให้พิมพ์ชื่อหุ้น
ticker_symbol = st.text_input("พิมพ์สัญลักษณ์หุ้น (เช่น AAPL, TSLA, PTT.BK สำหรับหุ้นไทย)", "AAPL")

# ใช้คำสั่งดึงข้อมูลจาก Yahoo Finance
ticker_data = yf.Ticker(ticker_symbol)

# ==========================================
# ส่วนที่ 1: ปุ่มเลือกช่วงเวลาและดึงข้อมูลประวัติ
# ==========================================
period_options = {
    "1 วัน": "1d", 
    "5 วัน": "5d", 
    "1 เดือน": "1mo", 
    "3 เดือน": "3mo", 
    "6 เดือน": "6mo", 
    "1 ปี": "1y", 
    "5 ปี": "5y"
}
selected_period = st.radio("เลือกระยะเวลาของกราฟเพื่อเปรียบเทียบราคา", list(period_options.keys()), horizontal=True)
period_value = period_options[selected_period]

# ปรับความละเอียดของกราฟ (Interval)
interval_value = "1d"
if period_value == "1d":
    interval_value = "5m" 
elif period_value == "5d":
    interval_value = "1h"

# ดึงข้อมูลประวัติราคาย้อนหลังมาเก็บไว้ก่อน
history = ticker_data.history(period=period_value, interval=interval_value)

# ==========================================
# ส่วนที่ 2: แสดงราคาปัจจุบัน และเปรียบเทียบกับอดีต
# ==========================================
info = ticker_data.info
current_price = info.get('currentPrice') or info.get('regularMarketPrice')

# หากดึงราคา Real-time ตรงๆ ไม่ได้ ให้ใช้ราคาล่าสุดจากกราฟแทน
if not current_price and not history.empty:
    current_price = history['Close'].iloc[-1]

if not history.empty and current_price:
    # ดึงราคาจาก "จุดเริ่มต้น" ของช่วงเวลาที่เลือก (เช่น ราคาเมื่อ 1 เดือนที่แล้ว)
    past_price = history['Close'].iloc[0]
    
    # คำนวณส่วนต่างและเปอร์เซ็นต์เทียบกับอดีต
    price_change = current_price - past_price
    percent_change = (price_change / past_price) * 100
    
    # จัดรูปแบบตัวเลขให้สวยงาม
    price_str = f"{current_price:,.2f}"
    delta_str = f"{price_change:+,.2f} ({percent_change:+,.2f}%)"
    
    # เช็คราคาหลังตลาดปิด
    post_market = info.get('postMarketPrice')
    if post_market:
         price_str += f" (ปิดตลาด: {post_market:,.2f})"
         
    # แสดงผลตัวเลข พร้อมเปลี่ยนข้อความ Label ไปตามช่วงเวลาที่กด
    st.metric(label=f"ราคาปัจจุบันเทียบกับ {selected_period}ที่แล้ว", value=price_str, delta=delta_str)
else:
    st.info("ไม่มีข้อมูลราคาเพื่อใช้เปรียบเทียบในขณะนี้")

st.divider() # เส้นคั่น

# ==========================================
# ส่วนที่ 3: แสดงกราฟราคาย้อนหลัง
# ==========================================
st.write(f"**กราฟราคาเส้น (Line Chart) ย้อนหลัง {selected_period}**")

if not history.empty:
    fig = go.Figure(data=[go.Scatter(
        x=history.index, 
        y=history['Close'], 
        mode='lines', 
        name='ราคาปิด',
        line=dict(color='#0068C9', width=2)
    )])
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        height=450,
        yaxis_title="ราคา",
        xaxis_title="วันที่ / เวลา" if period_value in ["1d", "5d"] else "วันที่",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("ไม่พบข้อมูลกราฟของหุ้นนี้ในช่วงเวลาที่เลือก")

# ==========================================
# ส่วนที่ 4: ดึงข่าวสารล่าสุด
# ==========================================
st.write("**📰 ข่าวสารล่าสุด**")
news = ticker_data.news

if news:
    for item in news[:5]:
        title = item.get('title', f'อ่านข่าวอัปเดตล่าสุดของ {ticker_symbol}')
        link = item.get('link', f'https://finance.yahoo.com/quote/{ticker_symbol}')
        st.write(f"- [{title}]({link})")
else:
    st.write("ไม่พบข่าวสารในขณะนี้")

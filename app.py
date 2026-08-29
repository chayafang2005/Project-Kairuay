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
# ส่วนที่ 1: แสดงราคาปัจจุบัน และเปอร์เซ็นต์การเปลี่ยนแปลง
# ==========================================
info = ticker_data.info

# พยายามดึงราคาปัจจุบันและราคาปิดวันก่อนหน้า
current_price = info.get('currentPrice') or info.get('regularMarketPrice')
previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')

if current_price and previous_close:
    # คำนวณส่วนต่างและเปอร์เซ็นต์
    price_change = current_price - previous_close
    percent_change = (price_change / previous_close) * 100
    
    # จัดรูปแบบตัวเลขให้แสดงผลสวยงาม
    price_str = f"{current_price:,.2f}"
    delta_str = f"{price_change:+,.2f} ({percent_change:+,.2f}%)"
    
    # เช็คราคาหลังตลาดปิด (After-hours) ถ้ามีข้อมูล
    post_market = info.get('postMarketPrice')
    if post_market:
         price_str += f" (ปิดตลาด: {post_market:,.2f})"
         
    # แสดงผลเป็นกล่องตัวเลขขนาดใหญ่
    st.metric(label=f"ราคาปัจจุบันของ {ticker_symbol}", value=price_str, delta=delta_str)
else:
    st.info("ไม่มีข้อมูลราคาแบบเรียลไทม์ในขณะนี้")

st.divider() # เส้นคั่น

# ==========================================
# ส่วนที่ 2: แสดงกราฟราคาย้อนหลัง
# ==========================================
# เพิ่มปุ่มเลือกช่วงเวลา 1 วัน และ 5 วัน
period_options = {
    "1 วัน": "1d", 
    "5 วัน": "5d", 
    "1 เดือน": "1mo", 
    "3 เดือน": "3mo", 
    "6 เดือน": "6mo", 
    "1 ปี": "1y", 
    "5 ปี": "5y"
}
selected_period = st.radio("เลือกระยะเวลาของกราฟ", list(period_options.keys()), horizontal=True)
period_value = period_options[selected_period]

# ปรับความละเอียดของกราฟ (Interval) ให้เหมาะสมกับช่วงเวลา
interval_value = "1d" # ค่าเริ่มต้นคือ 1 วันต่อ 1 จุด
if period_value == "1d":
    interval_value = "5m" # ถ้าดู 1 วัน ให้ใช้กราฟแท่งละ 5 นาที
elif period_value == "5d":
    interval_value = "1h" # ถ้าดู 5 วัน ให้ใช้กราฟแท่งละ 1 ชั่วโมง

st.write(f"**กราฟราคาเส้น (Line Chart) ย้อนหลัง {selected_period}**")
history = ticker_data.history(period=period_value, interval=interval_value)

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
# ส่วนที่ 3: ดึงข่าวสารล่าสุด
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

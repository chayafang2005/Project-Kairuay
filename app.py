import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import feedparser
import pandas as pd
from datetime import datetime

# ขยายหน้าจอเว็บให้กว้างขึ้น
st.set_page_config(page_title="Project Kairuay", layout="wide")

# ==========================================
# เมนูด้านข้างสำหรับเลือกหน้าเว็บ
# ==========================================
st.sidebar.title("📌 เมนูหลัก")
page = st.sidebar.radio("เลือกหน้า", ["📊 ค้นหาและดูกราฟรายตัว", "🇺🇸 หุ้นยอดฮิตตลาดอเมริกา (US Stocks List)"])

# ==========================================
# หน้าที่ 1: รายชื่อหุ้นทั้งหมดในตลาดอเมริกา (เลือกดูแล้วกดสลับมาดูได้)
# ==========================================
if page == "🇺🇸 หุ้นยอดฮิตตลาดอเมริกา (US Stocks List)":
    st.title("🇺🇸 คลังรายชื่อหุ้นยอดฮิตในตลาดสหรัฐอเมริกา")
    st.write("เลือกหุ้นจากตารางด้านล่าง หรือพิมพ์สัญลักษณ์เพื่อดูข้อมูลเชิงลึก")
    
    # สร้างตารางรายชื่อหุ้นตัวอย่างในตลาด US (สามารถเพิ่มรายชื่อหุ้นอื่นๆ ได้ตามต้องการ)
    us_stocks_data = {
        "Ticker": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "NFLX", "AMD", "INTC", "RKLB", "ONDS"],
        "Company Name": ["Apple Inc.", "Microsoft Corp.", "Alphabet Inc. (Google)", "Amazon.com Inc.", "NVIDIA Corp.", "Tesla Inc.", "Meta Platforms Inc.", "Netflix Inc.", "Advanced Micro Devices", "Intel Corp.", "Rocket Lab USA", "Ondas Holdings"],
        "Sector": ["Technology", "Technology", "Communication", "Consumer Cyclical", "Technology", "Consumer Cyclical", "Technology", "Communication", "Technology", "Technology", "Industrials", "Technology"]
    }
    df_stocks = pd.DataFrame(us_stocks_data)
    
    # แสดงตารางให้ผู้ใช้เลือก
    st.dataframe(df_stocks, use_container_width=True)
    
    st.info("💡 **วิธีใช้งาน:** นำชื่อย่อ (Ticker) เช่น AAPL หรือ NVDA ไปพิมพ์ค้นหาในหน้า **'ค้นหาและดูกราฟรายตัว'** ทางเมนูด้านซ้ายได้เลยครับ")

# ==========================================
# หน้าที่ 2: หน้าหลักเดิม (ค้นหา กราฟ ข่าว ข้อมูลหุ้น)
# ==========================================
elif page == "📊 ค้นหาและดูกราฟรายตัว":
    st.title("📈 คลังข้อมูลหุ้น Project Kairuay")

    # ช่องพิมพ์ชื่อหุ้น
    ticker_symbol = st.text_input("พิมพ์สัญลักษณ์หุ้น (เช่น AAPL, TSLA, ONDS, RKLB)", "RKLB")
    ticker_data = yf.Ticker(ticker_symbol)
    info = ticker_data.info

    # แบ่งหน้าจอเป็น 2 ฝั่ง (ซ้าย: กราฟและข่าว [สัดส่วน 2], ขวา: ข้อมูลหุ้น [สัดส่วน 1])
    main_col, info_col = st.columns([2, 1])

    # ฝั่งขวา: ข้อมูลเชิงลึกและลักษณะของหุ้น
    with info_col:
        st.markdown("### 📊 ข้อมูลสำคัญของหุ้น")
        
        company_name = info.get('longName') or ticker_symbol
        sector = info.get('sector', 'ไม่ระบุ')
        industry = info.get('industry', 'ไม่ระบุ')
        market_cap = info.get('marketCap')
        pe_ratio = info.get('trailingPE')
        high_52 = info.get('fiftyTwoWeekHigh')
        low_52 = info.get('fiftyTwoWeekLow')
        summary = info.get('longBusinessSummary', 'ไม่มีข้อมูลคำอธิบายบริษัทในขณะนี้')
        
        st.markdown(f"**ชื่อบริษัท:** {company_name}")
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

    # ฝั่งซ้าย: ราคา กราฟ และข่าวสาร
    with main_col:
        period_options = {"1 วัน": "1d", "5 วัน": "5d", "1 เดือน": "1mo", "3 เดือน": "3mo", "6 เดือน": "6mo", "1 ปี": "1y", "5 ปี": "5y"}
        selected_period = st.radio("เลือกระยะเวลา", list(period_options.keys()), horizontal=True)
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

        # แสดงราคาปัจจุบันและหลังปิดตลาด
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
            
            st.metric(label=f"ราคาปัจจุบันเทียบกับ {selected_period}ที่แล้ว", value=None, delta=delta_str)
            st.markdown(f"### {price_str}", unsafe_allow_html=True)

        # วาดกราฟแท่งเทียน
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
            st.warning("ไม่พบข้อมูลกราฟของหุ้นนี้")

        st.divider()

        # ส่วนข่าวสาร
        st.write("### 📰 LATEST NEWS & SUMMARY")

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

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import feedparser
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Project Kairuay", layout="wide")

# ตั้งค่าสถานะเริ่มต้นใน session_state
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "RKLB"

if 'current_page' not in st.session_state:
    st.session_state.current_page = "🇺🇸 หุ้นยอดฮิตตลาดอเมริกา (US Stocks List)"

default_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "NFLX", "AMD", "INTC", "RKLB", "ONDS"]

# เมนูด้านข้าง (ผูกกับ session_state เพื่อให้สลับหน้าได้ถูกต้อง)
st.sidebar.title("📌 เมนูหลัก")
page_options = ["🇺🇸 หุ้นยอดฮิตตลาดอเมริกา (US Stocks List)", "📊 ค้นหาและดูกราฟรายตัว"]

current_index = page_options.index(st.session_state.current_page) if st.session_state.current_page in page_options else 0
page = st.sidebar.radio("เลือกหน้า", page_options, index=current_index)
st.session_state.current_page = page

# ==========================================
# หน้าที่ 1: กระดานหุ้นยอดฮิตตลาดอเมริกา
# ==========================================
if page == "🇺🇸 หุ้นยอดฮิตตลาดอเมริกา (US Stocks List)":
    st.title("🇺🇸 กระดานหุ้นยอดฮิตตลาดสหรัฐอเมริกา (Real-time Market)")
    st.write("เลือกหุ้นที่คุณต้องการดูข้อมูลเชิงลึกจากเมนูด้านล่างนี้ได้ทันทีครับ")

    # ช่องเลือกหุ้นด่วนและปุ่มกดพุ่งไปหน้ากราฟ
    col_sel1, col_sel2 = st.columns([3, 1])
    with col_sel1:
        selected_btn = st.selectbox("🎯 เลือกหุ้นที่ต้องการดูข้อมูลด่วน:", default_tickers, index=default_tickers.index(st.session_state.selected_ticker) if st.session_state.selected_ticker in default_tickers else 0)
    with col_sel2:
        st.write("") # เว้นบรรทัดให้ตรงกับช่อง selectbox
        st.write("")
        if st.button("🚀 ไปดูข้อมูลเชิงลึก", use_container_width=True):
            st.session_state.selected_ticker = selected_btn
            st.session_state.current_page = "📊 ค้นหาและดูกราฟรายตัว"
            st.rerun()

    st.divider()
    
    search_query = st.text_input("🔍 ค้นหาหรือกรองชื่อหุ้นในตาราง", "")

    @st.cache_data(ttl=60)
    def get_market_data(tickers):
        data_list = []
        for t in tickers:
            try:
                tk = yf.Ticker(t)
                inf = tk.info
                name = inf.get('longName') or t
                sector = inf.get('sector', 'N/A')
                price = inf.get('currentPrice') or inf.get('regularMarketPrice') or 0
                prev_close = inf.get('previousClose') or inf.get('regularMarketPreviousClose') or price
                
                change = price - prev_close
                pct_change = (change / prev_close) * 100 if prev_close else 0
                
                post_market = inf.get('postMarketPrice')
                post_str = "-"
                if post_market:
                    post_change = post_market - price
                    post_pct = (post_change / price) * 100
                    sign_post = "+" if post_change >= 0 else ""
                    post_str = f"{post_market:,.2f} ({sign_post}{post_change:,.2f} | {sign_post}{post_pct:.2f}%)"

                data_list.append({
                    "Ticker": t,
                    "Company": name,
                    "Sector": sector,
                    "Price (USD)": round(price, 2),
                    "Change": round(change, 2),
                    "Change (%)": f"{pct_change:+.2f}%",
                    "After-Hours": post_str
                })
            except:
                continue
        return pd.DataFrame(data_list)

    with st.spinner("กำลังดึงข้อมูลราคาตลาดล่าสุด..."):
        df_market = get_market_data(default_tickers)

    if search_query:
        df_market = df_market[
            df_market['Ticker'].str.contains(search_query, case=False, na=False) |
            df_market['Company'].str.contains(search_query, case=False, na=False) |
            df_market['Sector'].str.contains(search_query, case=False, na=False)
        ]

    # ตารางแบบกดเลือกแถวเพื่อสลับหน้าอัตโนมัติ
    event = st.dataframe(
        df_market, 
        use_container_width=True, 
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    selected_rows = event.selection.get("rows", [])
    if selected_rows:
        row_index = selected_rows[0]
        chosen_ticker = df_market.iloc[row_index]["Ticker"]
        st.session_state.selected_ticker = chosen_ticker
        st.session_state.current_page = "📊 ค้นหาและดูกราฟรายตัว"
        st.rerun()

# ==========================================
# หน้าที่ 2: ค้นหาและดูกราฟรายตัว
# ==========================================
elif page == "📊 ค้นหาและดูกราฟรายตัว":
    st.title("📈 คลังข้อมูลหุ้นรายตัว Project Kairuay")

    ticker_symbol = st.text_input("พิมพ์สัญลักษณ์หุ้น (เช่น AAPL, TSLA, ONDS, RKLB)", st.session_state.selected_ticker)
    st.session_state.selected_ticker = ticker_symbol.upper()

    ticker_data = yf.Ticker(ticker_symbol)
    info = ticker_data.info

    main_col, info_col = st.columns([2, 1])

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

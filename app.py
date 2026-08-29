import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import feedparser
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Project Kairuay", layout="wide")

if 'search_ticker' not in st.session_state:
    st.session_state.search_ticker = "AAPL"

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["AAPL", "MSFT", "NVDA", "TSLA", "RKLB"]

st.title("📈 Project Kairuay: คลังข้อมูลและกราฟหุ้นสหรัฐฯ")

# ปรับสัดส่วนซ้ายให้แคบลง [0.8] และขวาให้กว้างขึ้น [3.2] เพื่อให้กราฟใหญ่ขึ้น
left_col, right_col = st.columns([0.8, 3.2])

# ==========================================
# ฝั่งซ้าย: รายการหุ้นที่ติดตาม (ปรับให้กระชับ)
# ==========================================
with left_col:
    st.subheader("⭐ หุ้นติดตาม")
    
    new_watch = st.text_input("➕ เพิ่มรหัส:", "").upper().strip()
    if new_watch:
        if new_watch not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_watch)
            st.rerun()

    st.write("---")
    
    for t in st.session_state.watchlist:
        try:
            tk = yf.Ticker(t)
            inf = tk.info
            price = inf.get('currentPrice') or inf.get('regularMarketPrice') or 0
            prev_close = inf.get('previousClose') or inf.get('regularMarketPreviousClose') or price
            change = price - prev_close
            pct = (change / prev_close) * 100 if prev_close else 0
            
            sign = "+" if pct >= 0 else ""
            btn_label = f"{t} | ${price:,.1f} ({sign}{pct:.1f}%)"
        except:
            btn_label = f"{t}"

        if st.button(btn_label, use_container_width=True, key=f"watch_btn_{t}"):
            st.session_state.search_ticker = t
            st.rerun()

    st.write("")
    remove_target = st.selectbox("🗑️ ลบหุ้น:", [""] + st.session_state.watchlist)
    if remove_target and st.button("ลบออก"):
        st.session_state.watchlist.remove(remove_target)
        st.rerun()

# ==========================================
# ฝั่งขวา: ข้อมูลบริษัท กราฟ และข่าวสาร (ขยายกว้างเต็มที่)
# ==========================================
with right_col:
    search_input = st.text_input("🔍 ค้นหาหุ้นตัวอื่นๆ ในตลาดสหรัฐฯ:", st.session_state.search_ticker).upper().strip()
    if search_input and search_input != st.session_state.search_ticker:
        st.session_state.search_ticker = search_input
        st.rerun()

    current_ticker = st.session_state.search_ticker
    ticker_data = yf.Ticker(current_ticker)
    info = ticker_data.info
    company_name = info.get('longName') or current_ticker

    is_watched = current_ticker in st.session_state.watchlist
    col_h1, col_h2 = st.columns([8, 2])
    with col_h1:
        st.markdown(f"## 🏢 {company_name} ({current_ticker})")
    with col_h2:
        st.write("")
        if is_watched:
            if st.button("★ เลิกติดตาม", use_container_width=True):
                st.session_state.watchlist.remove(current_ticker)
                st.rerun()
        else:
            if st.button("☆ ติดตามหุ้นนี้", use_container_width=True):
                if current_ticker not in st.session_state.watchlist:
                    st.session_state.watchlist.append(current_ticker)
                st.rerun()

    main_c, info_c = st.columns([2.5, 1])

    with info_c:
        st.markdown("### 📊 ข้อมูลสำคัญของหุ้น")
        sector = info.get('sector', 'ไม่ระบุ')
        industry = info.get('industry', 'ไม่ระบุ')
        market_cap = info.get('marketCap')
        pe_ratio = info.get('trailingPE')
        high_52 = info.get('fiftyTwoWeekHigh')
        low_52 = info.get('fiftyTwoWeekLow')
        summary = info.get('longBusinessSummary', 'ไม่มีข้อมูลคำอธิบายบริษัทในขณะนี้')
        
        st.markdown(f"**กลุ่มธุรกิจ:** {sector}")
        st.markdown(f"**อุตสาหกรรม:** {industry}")
        if market_cap:
            st.markdown(f"**มูลค่าตลาด:** {market_cap / 1e9:,.2f}B USD" if market_cap >= 1e9 else f"**มูลค่าตลาด:** {market_cap:,.2f} USD")
        st.markdown(f"**P/E Ratio:** {pe_ratio:,.2f}" if pe_ratio else "**P/E Ratio:** N/A")
        if high_52 and low_52:
            st.markdown(f"**52-Week High/Low:** {low_52:,.2f} - {high_52:,.2f}")
            
        st.markdown("---")
        st.markdown("**📖 ลักษณะธุรกิจ:**")
        st.markdown(f"<p style='color: #d0d0d0; font-size: 13px; line-height: 1.5;'>{summary[:450]}...</p>", unsafe_allow_html=True)

    with main_c:
        period_options = {"1 วัน": "1d", "5 วัน": "5d", "1 เดือน": "1mo", "3 เดือน": "3mo", "6 เดือน": "6mo", "1 ปี": "1y", "5 ปี": "5y"}
        selected_period = st.radio("เลือกระยะเวลา", list(period_options.keys()), horizontal=True, key="period_radio")
        period_value = period_options[selected_period]

        interval_value = "5m" if period_value == "1d" else ("1h" if period_value == "5d" else "1d")

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
                sign = "+" if post_change >= 0 else ""
                price_str += f' <span style="font-size:15px; color:gray;">(หลังปิดตลาด: {post_market:,.2f} <span style="color:{post_color};">{sign}{post_change:,.2f} [{sign}{post_percent:.2f}%]</span>)</span>'

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
                height=450,
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
    st.write(f"### 📰 LATEST NEWS & SUMMARY ({current_ticker})")
    rss_url = f"https://finance.yahoo.com/rss/headline?s={current_ticker}"
    feed = feedparser.parse(rss_url)

    if feed.entries:
        for entry in feed.entries[:5]:
            title = entry.get('title', 'ไม่มีหัวข้อข่าว')
            link = entry.get('link', '#')
            summary = entry.get('summary', 'คลิกที่หัวข้อเพื่ออ่านเนื้อหาฉบับเต็ม')
            publisher = entry.source.title if (hasattr(entry, 'source') and 'title' in entry.source) else "Yahoo Finance"
            
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

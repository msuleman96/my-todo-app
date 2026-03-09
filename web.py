import streamlit as st

import trading_agent


st.set_page_config(page_title="AI Trading Agent", layout="wide")

st.title("AI Trading Agent")
st.subheader("Stock recommendations with reasons")
st.write(
    "Enter stock symbols to get recommendations with stock name, live price, analysis, and buy/sell/hold reasoning."
)

if "ranked_results" not in st.session_state:
    st.session_state.ranked_results = []
if "last_error" not in st.session_state:
    st.session_state.last_error = ""
if "scan_ran" not in st.session_state:
    st.session_state.scan_ran = False

with st.form("scan_form"):
    symbols_input = st.text_area(
        "Watchlist symbols (comma-separated)",
        value="AAPL,MSFT,NVDA,AMZN,GOOGL,META,TSLA,AMD,AVGO,NFLX",
    )
    top_n = st.slider("How many top performers to analyze", min_value=3, max_value=20, value=8)
    webhook_url = st.text_input(
        "Optional webhook URL for alerts (Slack/Discord/Zapier)",
        type="password",
        help="If provided, BUY/SELL alerts can be sent automatically.",
    )
    submitted = st.form_submit_button("Run AI Scan")

if submitted:
    raw_symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
    st.session_state.scan_ran = True

    if not raw_symbols:
        st.session_state.ranked_results = []
        st.session_state.last_error = "Please provide at least one ticker symbol."
    else:
        with st.spinner("Analyzing market leaders and generating recommendations..."):
            ranked = trading_agent.rank_best_performing(raw_symbols, top_n=top_n)

        if not ranked:
            st.session_state.ranked_results = []
            st.session_state.last_error = "Could not fetch market data right now. Try again in a minute."
        else:
            st.session_state.ranked_results = ranked
            st.session_state.last_error = ""

if not st.session_state.scan_ran:
    st.info(
        "👋 Start by clicking **Run AI Scan**. Your recommendations will appear below and remain visible until your next scan."
    )

if st.session_state.last_error:
    st.error(st.session_state.last_error)

ranked_results = st.session_state.ranked_results
if ranked_results:
    st.markdown("## Recommendation Dashboard")
    table_rows = []
    alerts = []

    for stock in ranked_results:
        table_rows.append(
            {
                "Stock Name": stock.company_name,
                "Symbol": stock.symbol,
                "Signal": stock.signal,
                "Price": round(stock.close, 2),
                "Analysis": stock.analysis,
                "Reason": stock.reason,
            }
        )

        badge = "🟢" if stock.signal == "BUY" else "🔴" if stock.signal == "SELL" else "🟡"
        with st.container(border=True):
            st.markdown(f"### {badge} {stock.company_name} ({stock.symbol}) — **{stock.signal}**")
            st.write(f"**Price:** ${stock.close:.2f}")
            st.write(f"**Analysis:** {stock.analysis}")
            st.write(f"**Reason:** {stock.reason}")

        if stock.signal in {"BUY", "SELL"}:
            alerts.append(
                f"{stock.signal}: {stock.company_name} ({stock.symbol}) at ${stock.close:.2f}. "
                f"Reason: {stock.reason}"
            )

    st.markdown("### Snapshot Table")
    st.dataframe(table_rows, use_container_width=True)

    st.markdown("### Alerts")
    if alerts:
        for alert in alerts:
            st.info(alert)

        if webhook_url:
            sent_count = 0
            for alert in alerts:
                if trading_agent.send_webhook_alert(webhook_url, alert):
                    sent_count += 1

            if sent_count:
                st.success(f"Sent {sent_count}/{len(alerts)} alerts to webhook.")
            else:
                st.warning("Tried sending alerts but webhook delivery failed.")
    else:
        st.write("No immediate BUY/SELL alerts. Current leaders are mostly HOLD.")

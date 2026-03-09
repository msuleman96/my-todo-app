from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import requests


YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


@dataclass
class StockSignal:
    symbol: str
    company_name: str
    close: float
    one_month_return: float
    three_month_return: float
    six_month_return: float
    sma20: float
    sma50: float
    rsi14: float
    signal: str
    reason: str
    analysis: str


def _safe_pct_change(series: pd.Series, periods: int) -> float:
    if len(series) <= periods:
        return 0.0
    base = series.iloc[-periods - 1]
    if base == 0 or pd.isna(base):
        return 0.0
    return float((series.iloc[-1] / base - 1) * 100)


def _compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    gain = up.ewm(alpha=1 / window, adjust=False).mean()
    loss = down.ewm(alpha=1 / window, adjust=False).mean()
    rs = gain / loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))


def fetch_price_history(symbol: str, period: str = "1y", interval: str = "1d") -> tuple[pd.DataFrame, str]:
    """Fetch historical close prices and company name from Yahoo's chart endpoint."""
    url = YAHOO_CHART_URL.format(symbol=symbol)
    response = requests.get(
        url,
        params={"range": period, "interval": interval, "events": "history"},
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()

    result = payload.get("chart", {}).get("result", [])
    if not result:
        return pd.DataFrame(), symbol

    meta = result[0].get("meta", {})
    company_name = meta.get("longName") or meta.get("shortName") or symbol

    timestamps = result[0].get("timestamp") or []
    quote = result[0].get("indicators", {}).get("quote", [{}])[0]
    closes = quote.get("close", [])

    if not timestamps or not closes:
        return pd.DataFrame(), company_name

    df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(timestamps, unit="s", utc=True),
            "close": closes,
        }
    ).dropna()

    if df.empty:
        return df, company_name

    return df.set_index("datetime"), company_name


def evaluate_stock(symbol: str, company_name: str, history: pd.DataFrame) -> StockSignal | None:
    if history.empty or len(history) < 60:
        return None

    close = history["close"].astype(float)
    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1]
    rsi14 = _compute_rsi(close, 14).iloc[-1]

    one_m = _safe_pct_change(close, 21)
    three_m = _safe_pct_change(close, 63)
    six_m = _safe_pct_change(close, 126)

    if sma20 > sma50 and rsi14 < 70 and three_m > 0:
        signal = "BUY"
        reason = "Positive trend (SMA20 > SMA50), strong momentum, and no overbought warning."
    elif sma20 < sma50 or rsi14 > 75 or three_m < -8:
        signal = "SELL"
        reason = "Trend deterioration or overbought/weak momentum increases downside risk."
    else:
        signal = "HOLD"
        reason = "Indicators are mixed, so waiting for a stronger setup is safer."

    analysis = (
        f"{company_name} ({symbol}) is trading at ${close.iloc[-1]:.2f}. "
        f"Performance: 1M {one_m:.2f}%, 3M {three_m:.2f}%, 6M {six_m:.2f}%. "
        f"Trend: SMA20 {sma20:.2f} vs SMA50 {sma50:.2f}; RSI14 {rsi14:.2f}."
    )

    return StockSignal(
        symbol=symbol,
        company_name=company_name,
        close=float(close.iloc[-1]),
        one_month_return=one_m,
        three_month_return=three_m,
        six_month_return=six_m,
        sma20=float(sma20),
        sma50=float(sma50),
        rsi14=float(rsi14) if pd.notna(rsi14) else 50.0,
        signal=signal,
        reason=reason,
        analysis=analysis,
    )


def rank_best_performing(symbols: Iterable[str], top_n: int = 10) -> list[StockSignal]:
    scored: list[StockSignal] = []
    for symbol in symbols:
        try:
            history, company_name = fetch_price_history(symbol)
            stock = evaluate_stock(symbol, company_name, history)
            if stock:
                scored.append(stock)
        except requests.RequestException:
            continue

    scored.sort(key=lambda s: (s.six_month_return + s.three_month_return), reverse=True)
    return scored[:top_n]


def send_webhook_alert(webhook_url: str, message: str) -> bool:
    """Send buy/sell text to a webhook (Slack/Discord/Zapier/etc.)."""
    try:
        response = requests.post(webhook_url, json={"text": message}, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return False
    return True

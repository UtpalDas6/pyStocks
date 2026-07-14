"""Rank stocks by recent price momentum (% return over a lookback period)."""
import pandas as pd
import yfinance as yf


def _returns_from_closes(symbol_to_closes: dict) -> pd.DataFrame:
    rows = []
    for symbol, closes in symbol_to_closes.items():
        closes = closes.dropna()
        if len(closes) < 2:
            continue
        pct_return = (closes.iloc[-1] / closes.iloc[0] - 1) * 100
        rows.append({"symbol": symbol, "return_pct": round(float(pct_return), 2)})
    if not rows:
        return pd.DataFrame(columns=["symbol", "return_pct"])
    return pd.DataFrame(rows).sort_values("return_pct", ascending=False).reset_index(drop=True)


def fetch_momentum(symbols: list[str], period: str = "3mo") -> pd.DataFrame:
    """Return symbols ranked by % price return over `period`, highest first."""
    tickers = [f"{s}.NS" for s in symbols]
    data = yf.download(tickers, period=period, group_by="ticker", progress=False, threads=True)
    symbol_to_closes = {}
    for s in symbols:
        try:
            symbol_to_closes[s] = data[f"{s}.NS"]["Close"]
        except KeyError:
            pass
    return _returns_from_closes(symbol_to_closes)


def demo():
    synthetic = {
        "UP": pd.Series([100.0, 110.0, 130.0]),
        "DOWN": pd.Series([100.0, 90.0, 80.0]),
        "FLAT": pd.Series([100.0, 100.0, 100.0]),
    }
    df = _returns_from_closes(synthetic)
    assert list(df["symbol"]) == ["UP", "FLAT", "DOWN"]
    assert df.iloc[0]["return_pct"] == 30.0
    assert _returns_from_closes({}).empty
    print("momentum.py self-check ok")


if __name__ == "__main__":
    demo()

"""Promoter shareholding buy/sell signal logic."""
import requests
import pandas as pd

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}


def fetch_promoter_holding(symbol: str) -> pd.DataFrame:
    """Best-effort fetch of quarterly promoter holding % from NSE's public API.

    NSE aggressively blocks datacenter/cloud IPs, so this frequently fails when
    deployed. Callers should fall back to manual entry (see app.py) on error.
    """
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=5)
    resp = session.get(
        "https://www.nseindia.com/api/corporate-shareholding-pattern",
        params={"index": "equities", "symbol": symbol},
        headers=NSE_HEADERS,
        timeout=5,
    )
    resp.raise_for_status()
    rows = [
        {
            "quarter": entry.get("date") or entry.get("submissionDate"),
            "promoter_pct": float(entry.get("promoterAndPromoterGroup", 0) or 0),
        }
        for entry in resp.json().get("data", [])
    ]
    df = pd.DataFrame(rows)
    return df.sort_values("quarter").reset_index(drop=True) if not df.empty else df


def compute_signal(df: pd.DataFrame) -> tuple[str, float]:
    """BUY if promoter stake rose vs. the prior quarter, SELL if it fell, else HOLD."""
    if df is None or len(df) < 2:
        return "HOLD", 0.0
    delta = round(float(df["promoter_pct"].iloc[-1] - df["promoter_pct"].iloc[-2]), 4)
    if delta > 0:
        return "BUY", delta
    if delta < 0:
        return "SELL", delta
    return "HOLD", delta


def demo():
    assert compute_signal(pd.DataFrame({"promoter_pct": [50.0, 52.0]})) == ("BUY", 2.0)
    assert compute_signal(pd.DataFrame({"promoter_pct": [52.0, 50.0]})) == ("SELL", -2.0)
    assert compute_signal(pd.DataFrame({"promoter_pct": [50.0, 50.0]})) == ("HOLD", 0.0)
    assert compute_signal(pd.DataFrame({"promoter_pct": [50.0]})) == ("HOLD", 0.0)
    assert compute_signal(pd.DataFrame()) == ("HOLD", 0.0)
    print("promoter.py self-check ok")


if __name__ == "__main__":
    demo()

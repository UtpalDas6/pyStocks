"""Resolve a user-typed NSE stock symbol or company name to an NSE ticker."""
import yfinance as yf


def resolve_symbol(query: str) -> str | None:
    """Return an NSE symbol (no .NS suffix), or None if nothing matches.

    Tries the query as a literal symbol first (fast, exact). Falls back to
    Yahoo Finance's company search, which works for most full company names
    but can mis-rank short/ambiguous ones (e.g. "infosys" alone) — type the
    fuller name or the exact symbol in that case.
    """
    query = query.strip()
    if not query:
        return None

    candidate = query.upper().replace(" ", "")
    if not yf.Ticker(f"{candidate}.NS").history(period="5d").empty:
        return candidate

    try:
        results = yf.Search(query, max_results=8).quotes
    except Exception:
        results = []
    for r in results:
        if r.get("exchange") == "NSI" and r.get("quoteType") == "EQUITY":
            return r["symbol"].removesuffix(".NS")

    return None


def demo():
    assert resolve_symbol("TCS") == "TCS"
    assert resolve_symbol("tata consultancy") == "TCS"
    assert resolve_symbol("HDFC Bank") == "HDFCBANK"
    assert resolve_symbol("asdkjaskjd nonsense company") is None
    assert resolve_symbol("") is None
    print("lookup.py self-check ok")


if __name__ == "__main__":
    demo()

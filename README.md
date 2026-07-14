# pyStocks+

Stock analysis webapp: shows price history and a **BUY/SELL/HOLD** signal
derived from the promoter shareholding trend (rising promoter stake = BUY,
falling = SELL).

Promoter data is fetched live from NSE. If a symbol lookup fails (NSE
occasionally rate-limits or blocks a host), the app lets you enter the last
two quarters' promoter holding % manually instead (e.g. from screener.in or
NSE's site).

## Run locally
```
git clone <repo>
cd pyStocks
pip install -r requirements.txt
streamlit run main.py
```

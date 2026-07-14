# pyStocks+

Stock analysis webapp: shows price history and a **BUY/SELL/HOLD** signal
derived from the promoter shareholding trend (rising promoter stake = BUY,
falling = SELL).

NSE blocks live shareholding-pattern requests from most cloud/datacenter IPs,
so if the automatic fetch fails, the app lets you enter the last two
quarters' promoter holding % manually (e.g. from screener.in or NSE's site).

## Run locally
```
git clone <repo>
cd pyStocks
pip install -r requirements.txt
streamlit run main.py
```

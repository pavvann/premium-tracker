import requests
import pandas as pd

def get_binance_klines(symbol, interval, limit):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }
    response = requests.get(url, params=params)
    data = response.json()


    # turn raw data into DataFrame
    df = pd.DataFrame(data, columns= [
        "time", "open", "high", "low", "close", "volume",
        "_ignore1", "_ignore2", "_ignore3", "_ignore4", "_ignore5", "_ignore6"
    ])

    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df["close"] = df["close"].astype(float)
    return df[["time", "close"]]

def get_binance_perp_klines(symbol, interval, limit):
    url = "https://fapi.binance.com/fapi/v1/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }
    response = requests.get(url, params=params)
    data = response.json()


    # turn raw data into DataFrame
    df = pd.DataFrame(data, columns= [
        "time", "open", "high", "low", "close", "volume",
        "_ignore1", "_ignore2", "_ignore3", "_ignore4", "_ignore5", "_ignore6"
    ])

    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df["close"] = df["close"].astype(float)
    return df[["time", "close"]]

spot = get_binance_klines("BTCUSDT", "1d", 90)
perp = get_binance_perp_klines("BTCUSDT", "1d", 90)

print(spot.head())
print(perp.head())

df_merged = pd.merge(spot, perp, on="time", suffixes=("_spot", "_perp"))
# print(df_merged.head())

df_merged["basis"] = df_merged["close_perp"] - df_merged["close_spot"]
df_merged["basis_pct"] = (df_merged["basis"] / df_merged["close_spot"]) * 100

print(df_merged.head())
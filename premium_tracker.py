import requests
import pandas as pd
import matplotlib.pyplot as plt

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

spot = get_binance_klines("ETHUSDT", "1d", 90)
perp = get_binance_perp_klines("ETHUSDT", "1d", 90)

print(spot.head())
print(perp.head())

df_merged = pd.merge(spot, perp, on="time", suffixes=("_spot", "_perp"))
# print(df_merged.head())

df_merged["basis"] = df_merged["close_perp"] - df_merged["close_spot"]
df_merged["basis_pct"] = (df_merged["basis"] / df_merged["close_spot"]) * 100

print(df_merged.head())

df = df_merged.copy()
df['time'] = pd.to_datetime(df["time"])

static_threshold = 0.05

mean_pct = df['basis_pct'].mean()
std_pct = df["basis_pct"].std()
upper_dyn = mean_pct + 2*std_pct
lower_dyn = mean_pct - 2*std_pct

sig_up = df[df["basis_pct"] > static_threshold]
sig_down = df[df["basis_pct"] < -static_threshold]

fig, ax = plt.subplots(figsize=(12,5))
ax.plot(df['time'], df["basis_pct"], label="Basis (%)", linewidth = 1)

# static threshold lines
ax.axhline(static_threshold, linestyle=':', linewidth=1, label=f'Static +{static_threshold}%')
ax.axhline(-static_threshold, linestyle=':', linewidth=1, label=f'Static -{static_threshold}%')


# dynaminc threshold lines
ax.axhline(upper_dyn, linestyle='--', linewidth=1, label=f'Dyn upper (mean + 2sigma) = {upper_dyn: .4f}%')
ax.axhline(lower_dyn, linestyle='--', linewidth=1, label=f'Dyn lower (mean - 2sigma) = {lower_dyn: .4f}%')

ax.scatter(sig_up['time'], sig_up['basis_pct'], marker='^', s = 70, label='Static > +0.05%')
ax.scatter(sig_down['time'], sig_down['basis_pct'], marker='v', s = 70, label='Static < -0.05%')


ax.set_title("BTC Perpetual vs Spot - Basis (%)")
ax.set_xlabel('Date')
ax.set_ylabel('Basis (%)')
ax.legend(loc='best')
plt.xticks(rotation=25)
plt.tight_layout()
plt.show()


df['signal_static'] = 0
df.loc[df["basis_pct"] > static_threshold, 'signal_static'] = 1
df.loc[df["basis_pct"] < -static_threshold, 'signal_static'] = -1


# z-score
df['basis_z'] = (df['basis_pct'] - mean_pct) / std_pct
z_thresh = 2.0
df['signal_z'] = 0
df.loc[df["basis_z"] > z_thresh, 'signal_z'] = 1
df.loc[df["basis_z"] < -z_thresh, 'signal_z'] = -1


# quick summary
print("Static signals > +{:.3f}% :".format(static_threshold), len(df[df["signal_static"]==1]))
print("Static signals < -{:.3f}% :".format(static_threshold), len(df[df["signal_static"]==-1]))
print("Z-score signals (|z| > {:.1f}) :".format(z_thresh), len(df[df['signal_z']!=0]))


# actual rows for z-score signals
print(df.loc[df['signal_z']!=0, ['time', 'close_spot', 'close_perp', 'basis', 'basis_pct', 'basis_z', 'signal_z']])


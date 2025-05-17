import numpy as np
if not hasattr(np, "NaN"):          # NumPy 2.x uyumluluğu
    np.NaN = np.nan
import pandas as pd
import pandas_ta as ta

def sma(series, length=50):
    result = ta.sma(series, length=length)
    return None if result is None else result.iloc[-1]

def rsi(series, length=14):
    result = ta.rsi(series, length=length)
    if result is not None and not result.empty:
        return result.iloc[-1]
    return None  # veya 0, ya da raise Exception("RSI hesaplanamadı")

def macd(series, fast=12, slow=26, signal=9):
    out = ta.macd(series, fast=fast, slow=slow, signal=signal)
    return out['MACD_12_26_9'].iloc[-1], out['MACDs_12_26_9'].iloc[-1]

def atr(highs, lows, closes, length=14):
    result = ta.atr(high=highs, low=lows, close=closes, length=length)
    return None if result is None else result.iloc[-1]

def bollinger(series, length=20):
    out = ta.bbands(series, length=length)
    if out is None or out.empty:
        return None, None, None

    return (
        out[f"BBU_{length}_2.0"].iloc[-1],
        out[f"BBM_{length}_2.0"].iloc[-1],
        out[f"BBL_{length}_2.0"].iloc[-1],
    )
def stochastic(highs, lows, closes, k=14, d=3):
    result = ta.stoch(high=highs, low=lows, close=closes, k=k, d=d)
    if result is None or result.empty:
        return None, None
    return (
        result[f'STOCHk_{k}_{d}_{3}'].iloc[-1],
        result[f'STOCHd_{k}_{d}_{3}'].iloc[-1],
    )
def ema(series, length=20):
    result = ta.ema(series, length=length)
    return None if result is None else result.iloc[-1]
def cci(highs, lows, closes, length=20):
    result = ta.cci(high=highs, low=lows, close=closes, length=length)
    return None if result is None else result.iloc[-1]


def obv(close: pd.Series, volume: pd.Series):
    result = ta.obv(close=close, volume=volume)
    return result.iloc[-1] if result is not None and not result.empty else None

def adx(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14):
    result = ta.adx(high=high, low=low, close=close, length=length)
    if result is not None and not result.empty:
        return result['ADX_14'].iloc[-1]
    return None
def mfi(highs, lows, closes, volumes, length=14):
    result = ta.mfi(high=highs, low=lows, close=closes, volume=volumes, length=length)
    return result.iloc[-1] if result is not None and not result.empty else None
def roc(close_prices, length=12):
    result = ta.roc(close_prices, length=length)
    return result.iloc[-1] if result is not None and not result.empty else None

def williams_r(highs, lows, closes, length=14):
    result = ta.willr(high=highs, low=lows, close=closes, length=length)
    return result.iloc[-1] if result is not None and not result.empty else None

def ichimoku(highs, lows, closes):
    result = ta.ichimoku(high=pd.Series(highs), low=pd.Series(lows), close=pd.Series(closes))
    if result is None or result[0].empty:
        return None

    df = result[0]

    return {
        "tenkan_sen": df["ITS_9"].iloc[-1],
        "kijun_sen": df["IKS_26"].iloc[-1],   # DÜZELTİLDİ
        "senkou_span_a": df["ISA_9"].iloc[-1],  # DÜZELTİLDİ
        "senkou_span_b": df["ISB_26"].iloc[-1], # DÜZELTİLDİ
        "chikou_span": df["ICS_26"].iloc[-1],   # DÜZELTİLDİ
    }
def vwap(highs, lows, closes, volumes):
    import pandas as pd
    typical_price = (pd.Series(highs) + pd.Series(lows) + pd.Series(closes)) / 3
    tp_vol = typical_price * pd.Series(volumes)
    cum_tp_vol = tp_vol.cumsum()
    cum_vol = pd.Series(volumes).cumsum()

    if cum_vol.iloc[-1] == 0:
        return None

    return cum_tp_vol.iloc[-1] / cum_vol.iloc[-1]
def ultimate_oscillator(highs, lows, closes, s1=7, s2=14, s3=28):
    import pandas as pd

    highs = pd.Series(highs)
    lows = pd.Series(lows)
    closes = pd.Series(closes)

    bp = closes - pd.concat([lows, closes.shift(1)], axis=1).min(axis=1)
    tr = pd.concat([highs - lows, (highs - closes.shift(1)).abs(), (lows - closes.shift(1)).abs()], axis=1).max(axis=1)

    avg1 = bp.rolling(window=s1).sum() / tr.rolling(window=s1).sum()
    avg2 = bp.rolling(window=s2).sum() / tr.rolling(window=s2).sum()
    avg3 = bp.rolling(window=s3).sum() / tr.rolling(window=s3).sum()

    uo = 100 * (4 * avg1 + 2 * avg2 + avg3) / (4 + 2 + 1)

    return uo.iloc[-1] if not pd.isna(uo.iloc[-1]) else None




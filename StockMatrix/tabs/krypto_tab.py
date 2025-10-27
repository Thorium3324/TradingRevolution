# tabs/krypto_tab.py
# Bezpieczna, odporna na błędy wersja zakładki Krypto.
# Wklej ten plik do katalogu tabs/ i importuj krypto_tab() w app.py.
# Cel: nigdy nie powinno "wyjebać" całej strony z powodu błędów w tej zakładce.

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# opcjonalne: wskaźniki TA; obliczamy w try/except żeby nie przerwać aplikacji
try:
    from ta.trend import SMAIndicator, EMAIndicator, MACD
    from ta.momentum import RSIIndicator, StochasticOscillator
    from ta.volatility import BollingerBands, AverageTrueRange
    from ta.volume import OnBalanceVolumeIndicator
    TA_AVAILABLE = True
except Exception:
    # jeśli biblioteka ta nie jest dostępna lub ma inną strukturę, nie przerywamy działania
    TA_AVAILABLE = False

def krypto_tab():
    st.subheader("Zakładka Krypto — bezpieczna wersja")

    # INPUTS (unikalne klucze, żeby nie kolidowały z innymi zakładkami)
    ticker = st.text_input("Krypto ticker (np. BTC-USD):", "BTC-USD", key="krypto_ticker")
    start_date = st.date_input("Data początkowa:", pd.to_datetime("2023-01-01"), key="krypto_start")
    end_date = st.date_input("Data końcowa:", pd.Timestamp.today(), key="krypto_end")
    interval = st.selectbox("Interwał:", ["1d", "1h", "4h", "1wk"], index=0, key="krypto_interval")

    if not ticker:
        st.info("Wpisz ticker, aby zobaczyć dane.")
        return

    # Pobierz dane - zamknięte w try/except
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)
    except Exception as e:
        st.error(f"Błąd pobierania danych z yfinance: {e}")
        return

    if df is None or df.empty:
        st.warning(f"Brak danych dla {ticker} (yfinance zwrócił puste dane).")
        return

    # Upewnij się, że kolumny są płaskie (nie MultiIndex)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(map(str, c)).strip() for c in df.columns.values]

    # Konwersja typów i zabezpieczenia
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        except Exception:
            # jeśli konwersja się nie uda, zostawiamy kolumnę tak jak jest
            pass

    # Helpery
    def to_series_safe(x):
        """Zwraca pandas.Series 1D niezależnie od wejścia; może zwrócić pustą Series."""
        if x is None:
            return pd.Series(dtype="float64")
        if isinstance(x, pd.DataFrame):
            # wybierz pierwszą kolumnę z DataFrame
            try:
                return x.iloc[:, 0].astype("float64")
            except Exception:
                return pd.Series(dtype="float64")
        if isinstance(x, pd.Series):
            return x.astype("float64", errors="ignore")
        # próbuj skonwertować array/iterable
        try:
            return pd.Series(x).astype("float64")
        except Exception:
            return pd.Series(dtype="float64")

    def safe_float(x, default=0.0):
        try:
            if x is None:
                return default
            # jeśli NaN -> default
            if pd.isna(x):
                return default
            return float(x)
        except Exception:
            return default

    # Znajdź kolumny (dynamicznie, tolerancyjnie)
    def find_col(df, keyword):
        keyword = keyword.lower()
        for c in df.columns:
            if keyword in str(c).lower():
                return c
        return None

    open_col = find_col(df, "open")
    high_col = find_col(df, "high")
    low_col = find_col(df, "low")
    close_col = find_col(df, "close")
    volume_col = find_col(df, "volume")

    # Jeżeli kluczowych kolumn brak — nie przerywamy, tylko wyświetlamy komunikat i kończymy elegancko
    if not all([open_col, high_col, low_col, close_col]):
        st.warning("Dane nie zawierają pełnych kolumn Open/High/Low/Close. Zakładka krypto została wyłączona dla tego tickera.")
        return

    # Zamień na Series
    open_s = to_series_safe(df[open_col])
    high_s = to_series_safe(df[high_col])
    low_s = to_series_safe(df[low_col])
    close_s = to_series_safe(df[close_col])
    vol_s = to_series_safe(df[volume_col]) if volume_col else pd.Series(dtype="float64")

    # Usuń indeksy z NaN kluczowych wartości — ale nie usuwamy wszystkiego, tylko minimalne oczyszczenie
    non_na_idx = close_s.dropna().index
    if len(non_na_idx) == 0:
        st.warning("Brak wartości Close po przetworzeniu. Nie można wyświetlić wykresu.")
        return
    # Odfiltruj wszystkie series do zakresu dostępnych indexów
    df_proc = pd.DataFrame({
        "Open": open_s.reindex(close_s.index),
        "High": high_s.reindex(close_s.index),
        "Low": low_s.reindex(close_s.index),
        "Close": close_s.reindex(close_s.index),
        "Volume": vol_s.reindex(close_s.index)
    })
    # drop rows where Close is NaN
    df_proc = df_proc.dropna(subset=["Close"])
    if df_proc.empty:
        st.warning("Po odfiltrowaniu brak danych do wyświetlenia.")
        return

    # Bezpieczne przeliczenie wskaźników TA — każde w try/except
    # Jeśli biblioteka ta nie jest dostępna, wskaźniki będą puste (NaN)
    if TA_AVAILABLE:
        try:
            # upewnij się, że używamy 1D Series
            close_ser = to_series_safe(df_proc["Close"])
            high_ser = to_series_safe(df_proc["High"])
            low_ser = to_series_safe(df_proc["Low"])
            open_ser = to_series_safe(df_proc["Open"])
            vol_ser = to_series_safe(df_proc["Volume"])

            # Liczymy wskaźniki tylko jeśli mamy wystarczająco danych
            if len(close_ser) >= 1:
                try:
                    df_proc["SMA20"] = SMAIndicator(close_ser, 20).sma_indicator()
                except Exception:
                    df_proc["SMA20"] = np.nan
                try:
                    df_proc["SMA50"] = SMAIndicator(close_ser, 50).sma_indicator()
                except Exception:
                    df_proc["SMA50"] = np.nan
                try:
                    df_proc["SMA200"] = SMAIndicator(close_ser, 200).sma_indicator()
                except Exception:
                    df_proc["SMA200"] = np.nan
                try:
                    df_proc["EMA20"] = EMAIndicator(close_ser, 20).ema_indicator()
                except Exception:
                    df_proc["EMA20"] = np.nan
                try:
                    df_proc["EMA50"] = EMAIndicator(close_ser, 50).ema_indicator()
                except Exception:
                    df_proc["EMA50"] = np.nan
                try:
                    df_proc["RSI14"] = RSIIndicator(close_ser, 14).rsi()
                except Exception:
                    df_proc["RSI14"] = np.nan
                try:
                    macd = MACD(close_ser)
                    df_proc["MACD"] = macd.macd()
                    df_proc["MACD_signal"] = macd.macd_signal()
                except Exception:
                    df_proc["MACD"] = np.nan
                    df_proc["MACD_signal"] = np.nan
                try:
                    bb = BollingerBands(close_ser, window=20, window_dev=2)
                    df_proc["BB_upper"] = bb.bollinger_hband()
                    df_proc["BB_lower"] = bb.bollinger_lband()
                except Exception:
                    df_proc["BB_upper"] = np.nan
                    df_proc["BB_lower"] = np.nan
                try:
                    df_proc["ATR14"] = AverageTrueRange(high_ser, low_ser, close_ser, 14).average_true_range()
                except Exception:
                    df_proc["ATR14"] = np.nan
                try:
                    df_proc["Stochastic14"] = StochasticOscillator(high_ser, low_ser, close_ser, 14).stoch()
                except Exception:
                    df_proc["Stochastic14"] = np.nan
                try:
                    df_proc["OBV"] = OnBalanceVolumeIndicator(close_ser, vol_ser).on_balance_volume()
                except Exception:
                    df_proc["OBV"] = np.nan
            else:
                # za mało danych
                for col in ["SMA20","SMA50","SMA200","EMA20","EMA50","RSI14","MACD","MACD_signal",
                            "BB_upper","BB_lower","ATR14","Stochastic14","OBV"]:
                    df_proc[col] = np.nan
        except Exception:
            # jeśli coś pójdzie nie tak — ustawiamy wszystkie na NaN, ale nie przerywamy działania
            for col in ["SMA20","SMA50","SMA200","EMA20","EMA50","RSI14","MACD","MACD_signal",
                        "BB_upper","BB_lower","ATR14","Stochastic14","OBV"]:
                df_proc[col] = np.nan
    else:
        # TA nie jest dostępne — wypełniamy wskaźniki NaN, aplikacja dalej działa
        for col in ["SMA20","SMA50","SMA200","EMA20","EMA50","RSI14","MACD","MACD_signal",
                    "BB_upper","BB_lower","ATR14","Stochastic14","OBV"]:
            df_proc[col] = np.nan

    # WYKRES świecowy (Plotly) - wyświetlamy (na podstawie df_proc)
    try:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df_proc.index,
            open=df_proc["Open"],
            high=df_proc["High"],
            low=df_proc["Low"],
            close=df_proc["Close"],
            increasing_line_color='lime',
            decreasing_line_color='red',
            name="Świece"
        ))

        # nakładamy wskaźniki tylko jeśli kolumny istnieją i nie są całkowicie NaN
        def add_if_ok(name, col, color="orange"):
            if col in df_proc.columns and df_proc[col].dropna().shape[0] > 0:
                fig.add_trace(go.Scatter(x=df_proc.index, y=df_proc[col], line=dict(color=color, width=2), name=name))
        add_if_ok("SMA20", "SMA20", color="orange")
        add_if_ok("EMA20", "EMA20", color="green")
        add_if_ok("BB_upper", "BB_upper", color="red")
        add_if_ok("BB_lower", "BB_lower", color="red")
        fig.update_layout(title=f"{ticker} — Świece i wskaźniki", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Nie udało się narysować wykresu świecowego: {e}")

    # PANEL TECHNICAL ANALYSIS — bezpieczne wartości
    st.subheader("Technical Analysis (bezpiecznie)")
    def last_or_default(series, default=0.0):
        try:
            if series is None or not isinstance(series, (pd.Series, pd.DataFrame)):
                return default
            if isinstance(series, pd.DataFrame):
                series = series.iloc[:, 0]
            if series.empty:
                return default
            val = series.iloc[-1]
            return float(val) if pd.notna(val) else default
        except Exception:
            return default

    last_price = last_or_default(df_proc["Close"], 0.0)
    last_rsi = last_or_default(df_proc.get("RSI14"), 0.0)
    last_macd = last_or_default(df_proc.get("MACD"), 0.0)
    # volatility (30d) — tylko jeśli mamy min 2 wartości
    try:
        pct = df_proc["Close"].pct_change().dropna()
        vol30 = float(pct[-30:].std() * 100) if len(pct) >= 1 else 0.0
    except Exception:
        vol30 = 0.0

    cols = st.columns(4)
    cols[0].metric("Price (USD)", f"${last_price:.2f}", key="k_price")
    cols[1].metric("RSI (14)", f"{last_rsi:.2f}", key="k_rsi")
    cols[2].metric("MACD", f"{last_macd:.3f}", key="k_macd")
    cols[3].metric("Volatility (30d)", f"{vol30:.2f}%", key="k_vol")

    if vol30 > 10:
        st.warning("High volatility detected – expect larger price swings ⚠️")

    # Tabela ostatnich wartości (bezpiecznie, ograniczona do 100 wierszy)
    try:
        show_df = df_proc.tail(100).copy()
        # ukrywamy kolumny bardzo długie / niepotrzebne
        st.subheader("Ostatnie dane i obliczone wskaźniki (ograniczone do 100 wierszy)")
        st.dataframe(show_df)
    except Exception as e:
        st.info(f"Nie można wyświetlić tabeli: {e}")

    # Koniec funkcji — wszystko zabezpieczone tak, żeby zakładka nie wyrzucała błędów
    return

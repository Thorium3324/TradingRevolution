# --- AKCJE ---
if tabs=="Akcje":
    ticker = st.text_input("Ticker:", "AAPL").upper()
    start_date = st.date_input("Start:", date(2023,1,1))
    end_date = st.date_input("End:", date.today())
    
    if ticker:
        df = get_stock_data(ticker, start_date, end_date)
        if df is None or df.empty:
            st.warning(f"Brak danych dla {ticker}")
        else:
            df = add_technical_indicators(df)
            
            # --- Wykres świecowy z SMA/EMA ---
            fig_candle = go.Figure()
            fig_candle.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="Świece"
            ))
            fig_candle.add_trace(go.Scatter(
                x=df.index,
                y=df['SMA20'],
                line=dict(color='orange', width=2),
                name="SMA20"
            ))
            fig_candle.add_trace(go.Scatter(
                x=df.index,
                y=df['EMA20'],
                line=dict(color='green', width=2),
                name="EMA20"
            ))
            fig_candle.update_layout(
                title=f"Wykres świecowy {ticker} z SMA/EMA",
                xaxis_title="Data",
                yaxis_title="Cena",
                template="plotly_dark",
                height=600
            )
            
            # --- RSI ---
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(
                x=df.index,
                y=df['RSI'],
                line=dict(color='magenta', width=2),
                name="RSI"
            ))
            fig_rsi.update_layout(
                title="RSI (14)",
                xaxis_title="Data",
                yaxis_title="RSI",
                template="plotly_dark",
                height=250
            )
            
            # --- MACD ---
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(
                x=df.index,
                y=df['MACD'],
                line=dict(color='cyan', width=2),
                name="MACD"
            ))
            fig_macd.add_trace(go.Scatter(
                x=df.index,
                y=df['MACD_signal'],
                line=dict(color='yellow', width=2),
                name="MACD Signal"
            ))
            fig_macd.update_layout(
                title="MACD",
                xaxis_title="Data",
                yaxis_title="Wartość",
                template="plotly_dark",
                height=250
            )
            
            # --- Wyświetlanie w kolumnach ---
            st.plotly_chart(fig_candle, use_container_width=True)
            st.plotly_chart(fig_rsi, use_container_width=True)
            st.plotly_chart(fig_macd, use_container_width=True)

import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

DATA_FOLDER = "data/"
st.title("Dashboard Quant - Multi-Ticker & Indicateurs")

files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".parquet")]
tickers = [f.replace(".parquet", "") for f in files]

selected_tickers = st.multiselect("Tickers à afficher", tickers, default=tickers[:2])
window = st.slider("Période (rolling window)", 3, 50, 20)
deviation = st.slider("Écart-type pour Bollinger Bands", 1.0, 3.0, 2.0)

# Init des tableaux
chart_price = pd.DataFrame()
chart_sma = pd.DataFrame()
chart_vol = pd.DataFrame()
bollinger_upper = pd.DataFrame()
bollinger_lower = pd.DataFrame()

for ticker in selected_tickers:
    file = os.path.join(DATA_FOLDER, f"{ticker}.parquet")
    if os.path.exists(file):
        df = pd.read_parquet(file)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["timestamp"] = df["timestamp"].dt.floor("min")
        df = df.sort_values("timestamp").set_index("timestamp")

        price = df["price"].rename(ticker)
        sma = price.rolling(window=window).mean().rename(f"{ticker} SMA")
        vol = price.rolling(window=window).std()

        upper = (sma + deviation * vol).rename(f"{ticker} Upper Band")
        lower = (sma - deviation * vol).rename(f"{ticker} Lower Band")

        chart_price = chart_price.join(price, how="outer") if not chart_price.empty else price.to_frame()
        chart_sma = chart_sma.join(sma, how="outer") if not chart_sma.empty else sma.to_frame()
        chart_vol = chart_vol.join(vol.rename(f"{ticker} Vol"), how="outer") if not chart_vol.empty else vol.rename(f"{ticker} Vol").to_frame()
        bollinger_upper = bollinger_upper.join(upper, how="outer") if not bollinger_upper.empty else upper.to_frame()
        bollinger_lower = bollinger_lower.join(lower, how="outer") if not bollinger_lower.empty else lower.to_frame()

# Onglets
tab1, tab2, tab3, tab4 = st.tabs(["Prix", "SMA", "Volatilité", "Bollinger Bands"])

with tab1:
    st.subheader("Prix")
    st.line_chart(chart_price)

with tab2:
    st.subheader("Moyennes Mobiles (SMA)")
    st.line_chart(chart_sma)

with tab3:
    st.subheader("Volatilité glissante (rolling std)")
    st.line_chart(chart_vol)

with tab4:
    st.subheader("Bollinger Bands")

    for ticker in selected_tickers:
        try:
            price_col = chart_price[ticker]
            sma_col = chart_sma[f"{ticker} SMA"]
            upper_col = bollinger_upper[f"{ticker} Upper Band"]
            lower_col = bollinger_lower[f"{ticker} Lower Band"]

            # Fusion propre avec NaN clean
            df_bb = pd.concat([
                price_col.rename("Prix"),
                sma_col.rename("SMA"),
                upper_col.rename("Bande Supérieure"),
                lower_col.rename("Bande Inférieure")
            ], axis=1).dropna()

            if not df_bb.empty:
                st.write(f"**{ticker}**")

                fig = go.Figure()

                fig.add_trace(go.Scatter(x=df_bb.index, y=df_bb["Prix"], mode="lines", name="Prix"))
                fig.add_trace(go.Scatter(x=df_bb.index, y=df_bb["SMA"], mode="lines", name="SMA"))
                fig.add_trace(go.Scatter(x=df_bb.index, y=df_bb["Bande Supérieure"], mode="lines", name="Upper Band", line=dict(dash='dot')))
                fig.add_trace(go.Scatter(x=df_bb.index, y=df_bb["Bande Inférieure"], mode="lines", name="Lower Band", line=dict(dash='dot')))

                fig.update_layout(
                    height=400,
                    margin=dict(l=0, r=0, t=30, b=0),
                    legend=dict(orientation="h"),
                    title=f"{ticker} – Bollinger Bands",
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"{ticker} : Pas assez de données pour calculer les bandes.")

        except KeyError as e:
            st.warning(f"Colonnes manquantes pour {ticker} : {e}")






#streamlit run dashboard/app.py

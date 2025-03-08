import streamlit as st
import pandas as pd
import plotly.express as px

def main():
    st.title("IMDb Top 250 - Análise Interativa")
    df = pd.read_csv("imdb_top250.csv")
    
    st.header("Dados Brutos")
    st.dataframe(df)
    
    st.header("Visualizações")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Rating vs Votos")
        st.plotly_chart(px.scatter(df, x='rating', y='votes', color='year'))
    
    with col2:
        st.subheader("Distribuição por Ano")
        st.plotly_chart(px.histogram(df, x='year'))
    
    st.download_button("Baixar CSV", df.to_csv(), "imdb_top250.csv")

if __name__ == "__main__":
    main()
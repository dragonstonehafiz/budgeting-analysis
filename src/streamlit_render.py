import streamlit as st
import src.plots as plots
import pandas as pd

def render_comparison(df: pd.DataFrame, category_colors: dict):
    st.subheader("Comparison Across Years")
    st.plotly_chart(plots.plot_comparison_line(df), use_container_width=True)
    st.plotly_chart(plots.plot_comparison_bar(df, category_colors=category_colors), use_container_width=True)

def render_yearly(df: pd.DataFrame, selected_year: str, category_colors: dict):
    st.subheader(f"Showing All Plots for {selected_year}")
    
    st.plotly_chart(plots.plot_yearly_line(df, selected_year, category_colors=category_colors), use_container_width=True)
    st.plotly_chart(plots.plot_yearly_bar(df, selected_year, category_colors=category_colors), use_container_width=True)
    st.plotly_chart(plots.plot_yearly_pie(df, selected_year, category_colors=category_colors), use_container_width=True)
    

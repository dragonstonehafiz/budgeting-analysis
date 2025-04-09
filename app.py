import streamlit as st
from src.streamlit_init import init
from src.streamlit_render import render_yearly, render_comparison

# Page config
st.set_page_config(page_title="Spending Dashboard", layout="wide")

# Load data
df, category_colors = init()

# Sidebar: Year selection only
st.sidebar.header("Filter")
year_options = sorted(df['Year'].dropna().unique(), reverse=True)
selected_year = st.sidebar.selectbox("Select Year", year_options)


# Main: Dashboard title
st.title("Spending Dashboard")
comparison, yearly = st.tabs(["Comparison", "Yearly"])

with comparison:
    render_comparison(df, category_colors)
with yearly:
    render_yearly(df, selected_year, category_colors)



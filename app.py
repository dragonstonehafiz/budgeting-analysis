import streamlit as st
from src.streamlit_init import init
from src.streamlit_render import render_yearly, render_filter

# Page config
st.set_page_config(page_title="Spending Dashboard", layout="wide")

# Load data
df, category_colors = init()

# Sidebar: View selection
st.sidebar.header("View Options")
view_mode = st.sidebar.radio("Choose View", ["Full Data", "Yearly", "Search"])

# Sidebar: Year selection (only if Yearly view is active)
if view_mode == "Yearly":
    year_options = sorted(df['Year'].dropna().unique(), reverse=True)
    selected_year = st.sidebar.selectbox("Select Year", year_options)

# Render based on selected view
if view_mode == "Full Data":
    render_yearly(df, category_colors, full_data=True)
elif view_mode == "Yearly":
    render_yearly(df, category_colors, selected_year=selected_year, full_data=False)
elif view_mode == "Search":
    render_filter(df, category_colors)


import streamlit as st
import src.plots as plots
import pandas as pd

def render_yearly(df: pd.DataFrame, category_colors: dict, selected_year: str=None, full_data=True):
    st.header("Spending Insights")
    df = df.copy()
    
    # Filter year
    if not full_data:
        df = df[df['Year'] == selected_year]
        
    # Category to filter by
    category_options = df["Category"].dropna().unique()
    selected_category = st.multiselect("Category Filter", category_options, key="category_filter", default=category_options)
    if len(selected_category) > 0:
        df = df[df["Category"].isin(selected_category)]

    render_spending_summary(df, category_colors, full_data=full_data)
    render_category_breakdown(df, category_colors, full_data=full_data)
    render_insights(df, category_colors, full_data=full_data)

def render_top_items(df: pd.DataFrame, n: int = 10, reverse = False):
    if reverse:
        st.markdown(f"**Top {n} Least Expensive Items**")
    else:
        st.markdown(f"**Top {n} Most Expensive Items**")
    
    # Sort
    top_items = df.sort_values(by="Cost", ascending=reverse)
    # Drop duplicates by item name
    top_items = top_items.drop_duplicates(subset="Item")
    # Take top n
    top_items = top_items.head(n).reset_index(drop=True)
    st.dataframe(top_items[['Item', 'Cost', 'Category', 'Date']].style.format({"Cost": "${:,.2f}"}), use_container_width=True)

def render_spending_summary(df: pd.DataFrame, category_colors: dict, full_data=True):
    # --- GENERAL SECTION ---
    st.subheader("Spending Summary")
    
    st.plotly_chart(plots.plot_monthly_spend_by_category(df, category_colors=category_colors), use_container_width=True)

    # Totals by Month
    st.markdown("**Total Spending by Month**")
    month_totals = df.groupby(['MonthNum', 'Month'])['Cost'].sum().reset_index()
    month_totals = month_totals.sort_values('MonthNum').reset_index(drop=True)
    st.dataframe(month_totals[['Month', 'Cost']].style.format({"Cost": "${:,.2f}"}), use_container_width=True)
    

    # Render Category Data
    left, right = st.columns(2)
    with left:
        st.plotly_chart(plots.plot_spending_by_category_pie(df, category_colors=category_colors), use_container_width=True)
    with right:
        st.markdown("**Total Spending by Category**")
        category_totals = df.groupby('Category')['Cost'].sum().reset_index()
        category_totals = category_totals.sort_values(by='Cost', ascending=False).reset_index(drop=True)
        st.dataframe(category_totals.style.format({"Cost": "${:,.2f}"}), use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.markdown("**Top 10 Most Expensive Items by Category**")
        top_by_cat = df.sort_values(by='Cost', ascending=False).groupby('Category').head(1).reset_index(drop=True)
        st.dataframe(top_by_cat[['Category', 'Item', 'Cost']].style.format({"Cost": "${:,.2f}"}), use_container_width=True)
    with right:
        st.plotly_chart(plots.plot_avg_spend_per_category(df, category_colors=category_colors), use_container_width=True)
        
    # Render top and least expensive items
    render_top_items(df, 10)

    st.markdown("---")

def render_category_breakdown(df: pd.DataFrame, category_colors: dict, full_data=True):
    # --- CATEGORY SECTION ---
    st.subheader("Category Breakdown")
        
    # Category drilldown
    st.markdown("**Detailed View by Category**")
    category_options = df['Category'].dropna().unique()
    selected_category = st.selectbox("Choose a category to explore", category_options)

    # Filtered view
    df_cat = df[df['Category'] == selected_category]

    left, right = st.columns(2)
    
    with left:
        # Top purchases in that category
        st.markdown("Top Purchases Table")
        top_cat_items = df_cat.sort_values(by="Cost", ascending=False).head(10).reset_index(drop=True)
        st.dataframe(top_cat_items[['Item', 'Cost', 'Date']].style.format({"Cost": "${:,.2f}"}), use_container_width=True)
    with right:
        st.markdown("Top Purchases Chart")
        st.plotly_chart(plots.plot_top_items_in_category(df_cat), use_container_width=True)
        
    left, right = st.columns(2)
    
    if not full_data:
        with left:
            st.markdown("Monthly Spending in Selected Category")
            st.plotly_chart(plots.plot_monthly_spending_in_category(df_cat), use_container_width=True)
        with right:
            # Monthly totals for that category
            st.markdown("Monthly Spending in Selected Category")
            cat_monthly = df_cat.groupby(['MonthNum', 'Month'])['Cost'].sum().reset_index()
            cat_monthly = cat_monthly.sort_values('MonthNum').reset_index(drop=True)
            st.dataframe(cat_monthly[['Month', 'Cost']].style.format({"Cost": "${:,.2f}"}), use_container_width=True)
        
    st.markdown("---")


def render_insights(df: pd.DataFrame, category_colors: dict, full_data=True):
    # --- INSIGHTS SECTION ---
    st.subheader("Insights")

    st.plotly_chart(plots.plot_cost_scatter(df), use_container_width=True)
    
    # Sneaky Totals (cheap items that added up)
    st.markdown("**Sneaky Totals** — Low-cost items that quietly piled up")
    sneaky = df[df['Cost'] < 10]
    sneaky_summary = sneaky.groupby('Item').agg(
        Count=('Cost', 'count'),
        Total_Spent=('Cost', 'sum')
    ).query('Total_Spent > 50').sort_values(by='Total_Spent', ascending=False).reset_index()
    st.dataframe(sneaky_summary.style.format({"Total_Spent": "${:,.2f}"}), use_container_width=True)

    if not full_data:
        # New Recurring Items
        st.markdown("**New Recurring Items** — Things you started buying a lot this year")
        first_half = df[df['MonthNum'] <= 6]
        second_half = df[df['MonthNum'] > 6]
        recurring_late = second_half.groupby('Item').filter(lambda x: len(x) > 3)
        recurring_early = first_half['Item'].unique()
        new_recurring = recurring_late[~recurring_late['Item'].isin(recurring_early)]
        new_summary = new_recurring.groupby('Item').agg(
            Count=('Cost', 'count'),
            Total_Spent=('Cost', 'sum')
        ).sort_values(by='Count', ascending=False).reset_index()
        st.dataframe(new_summary.style.format({"Total_Spent": "${:,.2f}"}), use_container_width=True)

    if not full_data:
        # Top Category per Month
        st.markdown("**Top Category per Month** — Which category dominated each month?")
        monthly_totals = df.groupby(['MonthNum', 'Month', 'Category'])['Cost'].sum().reset_index()
        monthly_winners = (
            monthly_totals
            .sort_values(['MonthNum', 'Cost'], ascending=[True, False])
            .drop_duplicates(['MonthNum'])
        )
        monthly_winners = monthly_winners.sort_values('MonthNum').reset_index(drop=True)
        top_category_table = monthly_winners[['Month', 'Category', 'Cost']]
        st.dataframe(top_category_table.style.format({"Cost": "${:,.2f}"}), use_container_width=True)

    # Single Large Purchases
    threshold = df['Cost'].mean() + df['Cost'].std()
    st.markdown(f"**Single Large Purchases** — One-time purchases over ${threshold:.2f}")
    large_purchases = df[df['Cost'] >= threshold]
    item_counts = large_purchases['Item'].value_counts()
    single_large = large_purchases[large_purchases['Item'].isin(item_counts[item_counts == 1].index)]
    single_large_table = single_large[['Item', 'Category', 'Cost', 'Date']].sort_values(by='Cost', ascending=False).reset_index(drop=True)
    st.dataframe(single_large_table.style.format({"Cost": "${:,.2f}"}), use_container_width=True)
    
    
    # Recurring Items (5+ times)
    st.markdown("**Recurring Items (Bought 5+ Times)**")
    recurring = df.groupby('Item').filter(lambda x: len(x) > 5)
    recurring_summary = recurring.groupby('Item').agg(
        Count=('Cost', 'count'),
        Total_Spent=('Cost', 'sum')
    ).sort_values(by='Count', ascending=False).reset_index()
    st.dataframe(recurring_summary.style.format({"Total_Spent": "${:,.2f}"}), use_container_width=True)


def render_filter(df: pd.DataFrame, category_colors: dict):
    # --- FILTER SECTION ---
    st.subheader("Statistics")
    
    left, right = st.columns(2)
    with left:
        render_top_items(df, 5)
    with right:
        render_top_items(df, 5, reverse=True)
    
    # Calculate statistics
    stats = {
        "Most Expensive": df["Cost"].max(),
        "Least Expensive": df["Cost"].min(),
        "Mean": df["Cost"].mean(),
        "Median": df["Cost"].median(),
        "25th Percentile (Lower)": df["Cost"].quantile(0.25),
        "75th Percentile (Upper)": df["Cost"].quantile(0.75),
        "Standard Deviation": df["Cost"].std()
    }
    stats_df = pd.DataFrame(stats.items(), columns=["Statistic", "Value"])
    st.dataframe(stats_df.style.format({"Value": "${:,.2f}"}), use_container_width=True)
    
    st.subheader("Filter Parameters")
    
    # Terms to include and exclude
    left, right = st.columns(2)
    with left:
        include_term = st.text_input("Include Term", key="item_name", help="Searches for items that include this search term")
    with right:
        exclude_term = st.text_input("Exclude Term", key="exclude_name", help="Excludes items that include this term")
    
    # Category to filter by
    category_options = df["Category"].dropna().unique()
    selected_category = st.multiselect("Category Filter", category_options, key="category_filter")
    
    # Filter by category and date
    left, right = st.columns(2)
    with left:
        min_date = df["Date"].min()
        # Add Start and End Date pickers
        start_date = st.date_input("Start Date", value=min_date, help=f"Earliest date in your data is {min_date}")
    with right:
        max_date = df["Date"].max()
        end_date = st.date_input("End Date", value=max_date, help=f"Latest date in your data is {max_date}")
        
    # Optionally: Validate that end_date is not before start_date
    if start_date > end_date:
        st.error("End date must be after start date.")
        
    # Add minimum and maximum cost filters
    min_cost = df["Cost"].min()
    max_cost = df["Cost"].max()
    min_cost, max_cost = st.slider("Select Cost Range", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost), key="cost_range")
    
    filtered_df = df.copy()
    
    # Filter by name
    if len(include_term) > 1:
        filtered_df = df[df["Item"].str.contains(include_term, case=False)]
    if len(exclude_term) > 1:
        filtered_df = filtered_df[~filtered_df["Item"].str.contains(exclude_term, case=False, na=False)]
        
    # Filter by category
    if len(selected_category) >0:
        filtered_df = filtered_df[filtered_df["Category"].isin(selected_category)]
        
    # Filter by date
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df["Date"] >= pd.to_datetime(start_date)) &
            (filtered_df["Date"] <= pd.to_datetime(end_date))
        ]
        
    # Filter By Cost
    filtered_df = filtered_df[
        (filtered_df["Cost"] >= min_cost) &
        (filtered_df["Cost"] <= max_cost)
    ]
    
    st.subheader("Filtered Data")
    
    # Render Category Data
    left, right = st.columns(2)
    with left:
        st.plotly_chart(plots.plot_spending_by_category_pie(filtered_df, category_colors=category_colors), use_container_width=True)
    with right:
        st.markdown("**Total Spending by Category**")
        category_totals = filtered_df.groupby('Category')['Cost'].sum().reset_index()
        category_totals = category_totals.sort_values(by='Cost', ascending=False).reset_index(drop=True)
        st.dataframe(category_totals.style.format({"Cost": "${:,.2f}"}), use_container_width=True)
    
    st.dataframe(filtered_df[['Item', 'Category', 'Cost', 'Date']], use_container_width=True)
    
    render_insights(filtered_df, category_colors=category_colors, full_data=True)
    

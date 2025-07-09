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
    render_statistics(df)
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
    st.dataframe(top_items[['Item', 'Cost', 'Category', 'Date', "Notes"]].style.format({"Cost": "${:,.2f}"}), use_container_width=True, hide_index=True)

def render_spending_summary(df: pd.DataFrame, category_colors: dict, full_data=True):
    # --- GENERAL SECTION ---
    st.subheader("Spending Summary")
    
    if not full_data:
        left, right = st.columns([0.2, 0.8])
        
        with left:
            # Totals by Month
            st.markdown("**Total Spending by Month**")
            month_totals = df.groupby(['MonthNum', 'Month'])['Cost'].sum().reset_index()
            month_totals = month_totals.sort_values('MonthNum').reset_index(drop=True)
            st.dataframe(month_totals[['Month', 'Cost']].style.format({"Cost": "${:,.2f}"}), use_container_width=True, hide_index=True, height=455)
        
        with right:
            # ----- Choose which trend plot to display ------------------------------------
            plot_options = {
                "Overall monthly spending": lambda d: plots.plot_spend_trend_line_month_and_category(
                    d, category_colors=category_colors, category=False),
                "Monthly spending by category": lambda d: plots.plot_spend_trend_line_month_and_category(
                    d, category_colors=category_colors, category=True
                ),
            }

            choice = st.selectbox(
                "Select trend view", 
                options=list(plot_options.keys())
            )

            # Generate and display the chosen figure
            fig = plot_options[choice](df)
            st.plotly_chart(fig, use_container_width=True)
            
        st.markdown("**Items Bought this Month**")
        selected_month = st.selectbox("Month", options=df['Month'].unique())
        month_items = df.loc[df['Month'] == selected_month]
        month_items = month_items[['Item', 'Category', 'Cost', 'Date', "Notes"]]
        st.dataframe(month_items, hide_index=True)
    else:
        filtered_df = df[['Item', 'Category', 'Cost', 'Date', "Notes"]]
        # ----- Choose which trend plot to display ------------------------------------
        
        plot_options = {
            "Spending Trend Line (Month by Month)": lambda d: plots.plot_spend_trend_line_monthly(
                d, category_colors=category_colors, category=False),
            "Spending Trend Line (Month by Month) (Category)": lambda d: plots.plot_spend_trend_line_monthly(
                d, category_colors=category_colors, category=True),
            "Monthly Spending (Seperated by Year)": lambda d: plots.plot_spend_trend_line_month_and_year(d)
        }

        choice = st.selectbox(
            "Select trend view", 
            options=list(plot_options.keys())
        )

        # Generate and display the chosen figure
        fig = plot_options[choice](df)
        st.plotly_chart(fig, use_container_width=True)
    

    # Render Category Data
    left, right = st.columns([0.7, 0.3])
    with left:
        st.plotly_chart(plots.plot_spending_by_category_pie(df, category_colors=category_colors), use_container_width=True)
    with right:
        st.markdown("**Total Spending by Category**")
        category_totals = df.groupby('Category')['Cost'].sum().reset_index()
        category_totals = category_totals.sort_values(by='Cost', ascending=False).reset_index(drop=True)
        st.dataframe(category_totals.style.format({"Cost": "${:,.2f}"}), use_container_width=True, hide_index=True)

    left, right = st.columns([0.3, 0.7])
    with left:
        st.markdown("**Top 10 Most Expensive Items by Category**")
        top_by_cat = df.sort_values(by='Cost', ascending=False).groupby('Category').head(1).reset_index(drop=True)
        st.dataframe(top_by_cat[['Category', 'Item', 'Cost', "Notes"]].style.format({"Cost": "${:,.2f}"}), use_container_width=True, hide_index=True)
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

    left, right = st.columns([0.3, 0.7])
    
    with left:
        # Top purchases in that category
        st.markdown("Top Purchases Table")
        top_cat_items = df_cat.sort_values(by="Cost", ascending=False).head(10).reset_index(drop=True)
        st.dataframe(top_cat_items[['Item', 'Cost', 'Date', "Notes"]].style.format({"Cost": "${:,.2f}"}), use_container_width=True, hide_index=True)
    with right:
        st.markdown("Top Purchases Chart")
        st.plotly_chart(plots.plot_top_items_in_category(df_cat), use_container_width=True)
        
    left, right = st.columns([0.7, 0.3])
    
    if not full_data:
        with left:
            st.markdown("Monthly Spending in Selected Category")
            st.plotly_chart(plots.plot_monthly_spending_in_category(df_cat), use_container_width=True)
        with right:
            # Monthly totals for that category
            st.markdown("Monthly Spending in Selected Category")
            cat_monthly = df_cat.groupby(['MonthNum', 'Month'])['Cost'].sum().reset_index()
            cat_monthly = cat_monthly.sort_values('MonthNum').reset_index(drop=True)
            st.dataframe(cat_monthly[['Month', 'Cost']].style.format({"Cost": "${:,.2f}"}), use_container_width=True, hide_index=True, height=455)
        
    st.markdown("---")


def render_insights(df: pd.DataFrame, category_colors: dict, full_data=True):
    # --- INSIGHTS SECTION ---
    st.subheader("Insights")
    
    # Sneaky Totals (cheap items that added up)
    st.markdown("**Sneaky Totals** — Low-cost items that quietly piled up")
    sneaky = df[df['Cost'] < 10]
    sneaky_summary = sneaky.groupby('Item').agg(
        Count=('Cost', 'count'),
        Total_Spent=('Cost', 'sum')
    ).query('Total_Spent > 50').sort_values(by='Total_Spent', ascending=False).reset_index()
    st.dataframe(sneaky_summary.style.format({"Total_Spent": "${:,.2f}"}), use_container_width=True, hide_index=True)

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
        st.dataframe(new_summary.style.format({"Total_Spent": "${:,.2f}"}), use_container_width=True, hide_index=True)

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
        st.dataframe(top_category_table.style.format({"Cost": "${:,.2f}"}), use_container_width=True, hide_index=True)

    # Single Large Purchases
    threshold = df['Cost'].mean() + df['Cost'].std()
    st.markdown(f"**Single Large Purchases** — One-time purchases over ${threshold:.2f}")
    large_purchases = df[df['Cost'] >= threshold]
    item_counts = large_purchases['Item'].value_counts()
    single_large = large_purchases[large_purchases['Item'].isin(item_counts[item_counts == 1].index)]
    single_large_table = single_large[['Item', 'Category', 'Cost', 'Date', "Notes"]].sort_values(by='Cost', ascending=False).reset_index(drop=True)
    st.dataframe(single_large_table.style.format({"Cost": "${:,.2f}"}), use_container_width=True, hide_index=True)
    
    
    # Recurring Items (5+ times)
    st.markdown("**Recurring Items (Bought 5+ Times)**")
    recurring = df.groupby('Item').filter(lambda x: len(x) > 3)
    recurring_summary = recurring.groupby('Item').agg(
        Count=('Cost', 'count'),
        Total_Spent=('Cost', 'sum')
    ).sort_values(by='Count', ascending=False).reset_index()
    st.dataframe(recurring_summary.style.format({"Total_Spent": "${:,.2f}"}), use_container_width=True, hide_index=True)


def render_filter(df: pd.DataFrame, category_colors: dict):
    render_statistics(df)
    
    # --- FILTER SECTION ---
    st.subheader("Filter Parameters")
    
    # Terms to include and exclude
    left, right = st.columns(2)
    with left:
        include_term = st.text_input("Include Term", key="item_name", help="Searches for items that include this search term")
    with right:
        exclude_term = st.text_input("Exclude Term", key="exclude_name", help="Excludes items that include this term")
    
    # Category to filter by
    category_options = df["Category"].dropna().unique()
    selected_category = st.multiselect("Category Filter", category_options, key="category_filter", default=category_options)
    
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
        st.dataframe(category_totals.style.format({"Cost": "${:,.2f}"}), use_container_width=True, hide_index=True)
    
    # Display all items in the filtered df
    st.dataframe(filtered_df[['Item', 'Category', 'Cost', 'Date', "Notes"]], use_container_width=True, hide_index=True)
    
    # Display spending from month to month
    st.plotly_chart(plots.plot_spend_trend_line_monthly(filtered_df), use_container_width=True)
    
    render_insights(filtered_df, category_colors=category_colors, full_data=True)
    
def render_statistics(df: pd.DataFrame):
    st.subheader("Statistics")
    
    left, right = st.columns(2)
    with left:
        render_top_items(df, 5)
    with right:
        render_top_items(df, 5, reverse=True)
    
    total_spent = df["Cost"].sum()
    most_expensive = df["Cost"].max()
    least_expensive = df["Cost"].min()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spent", f"${total_spent:,.2f}")
    col2.metric("Most Expensive", f"${most_expensive:,.2f}")
    col3.metric("Least Expensive", f"${least_expensive:,.2f}")
    
    mean = df["Cost"].mean()
    median = df["Cost"].median()
    std = df["Cost"].std()
    col1, col2, col3 = st.columns(3)
    col1.metric("Mean", f"${mean:,.2f}")
    col2.metric("Median", f"${median:,.2f}")
    col3.metric("Standard Deviation", f"${std:,.2f}")
    
    percentile_25th = df["Cost"].quantile(0.25)
    percentile_75th = df["Cost"].quantile(0.75)
    col1, col2, col3 = st.columns(3)
    col1.metric("25th Percentile", 
                f"${percentile_25th:,.2f}", 
                help="Lower quartile: 25 % of transactions cost **less** than this amount.")
    col3.metric("75th Percentile", 
                f"${percentile_75th:,.2f}",
                help="Upper quartile: 75 % of transactions cost **this amount or less**—only the most-expensive 25 % exceed it.")
    

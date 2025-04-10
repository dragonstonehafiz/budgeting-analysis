import streamlit as st
import src.plots as plots
import pandas as pd

def render_yearly(df: pd.DataFrame, category_colors: dict, selected_year: str=None, full_data=True):
    st.header("Spending Insights")
    df = df.copy()
    
    if not full_data:
        df = df[df['Year'] == selected_year]

    # --- GENERAL SECTION ---
    st.subheader("Spending Summary")
    
    st.plotly_chart(plots.plot_monthly_spend_by_category(df, category_colors=category_colors), use_container_width=True)

    # Top 10 Most Expensive Items
    st.markdown("**Top 10 Most Expensive Items**")
    top_items = df.sort_values(by="Cost", ascending=False).head(10).reset_index(drop=True)
    st.dataframe(top_items[['Item', 'Cost', 'Category', 'Date']].style.format({"Cost": "${:,.2f}"}), use_container_width=True)

    left, right = st.columns(2)
    
    with left:
        # Recurring Items (5+ times)
        st.markdown("**Recurring Items (Bought 5+ Times)**")
        recurring = df.groupby('Item').filter(lambda x: len(x) > 5)
        recurring_summary = recurring.groupby('Item').agg(
            Count=('Cost', 'count'),
            Total_Spent=('Cost', 'sum')
        ).sort_values(by='Count', ascending=False).reset_index()
        st.dataframe(recurring_summary.style.format({"Total_Spent": "${:,.2f}"}), use_container_width=True)

    with right:
        # Totals by Month
        st.markdown("**Total Spending by Month**")
        month_totals = df.groupby(['MonthNum', 'Month'])['Cost'].sum().reset_index()
        month_totals = month_totals.sort_values('MonthNum').reset_index(drop=True)
        st.dataframe(month_totals[['Month', 'Cost']].style.format({"Cost": "${:,.2f}"}), use_container_width=True)

    st.markdown("---")

    # --- CATEGORY SECTION ---
    st.subheader("Category Breakdown")

    left, right = st.columns(2)

    with left:
        st.plotly_chart(plots.plot_spending_by_category_pie(df, category_colors=category_colors), use_container_width=True)
    with right:
        st.markdown("**Total by Category**")
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
        

    # Category drilldown
    st.markdown("**Detailed View by Category**")
    category_options = sorted(df['Category'].dropna().unique())
    selected_category = st.selectbox("Choose a category to explore", category_options)

    # Filtered view
    df_cat = df[df['Category'] == selected_category]

    left, right = st.columns(2)
    
    with left:
        # Top purchases in that category
        st.markdown("Most Expensive Purchases in Selected Category")
        top_cat_items = df_cat.sort_values(by="Cost", ascending=False).head(10).reset_index(drop=True)
        st.dataframe(top_cat_items[['Item', 'Cost', 'Date']].style.format({"Cost": "${:,.2f}"}), use_container_width=True)

    with right:
        st.markdown("Most Expensive Purchases in Selected Category")
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
    
    # --- INSIGHTS SECTION ---
    st.subheader("Insights")

    st.markdown("**Item Cost Distribution** — How your spending is spread out across purchases")
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
    
    
    # No-Spend Categories
    if not full_data:
        st.markdown("**No-Spend Categories** — Where you spent absolutely nothing")
        all_categories = df['Category'].dropna().unique()
        spent_categories = df['Category'].unique()
        no_spend = sorted(set(all_categories) - set(spent_categories))
        if no_spend:
            st.write(", ".join(no_spend))
        else:
            st.success("You spent in every category this year!")

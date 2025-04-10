import plotly.express as px
import pandas as pd

def plot_monthly_trends_by_category(df: pd.DataFrame, year: int, category_colors=None):
    # Step 1: Create full Month + Category grid
    df_year = df[df['Year'] == year]
    all_months = df_year[['MonthNum', 'Month']].drop_duplicates()
    all_categories = df_year['Category'].drop_duplicates()
    month_category_grid = all_months.merge(all_categories, how='cross')

    # Step 2: Actual totals
    actual_totals = df_year.groupby(['MonthNum', 'Month', 'Category'])['Cost'].sum().reset_index()

    # Step 3: Merge and fill missing with zero
    filled_totals = month_category_grid.merge(actual_totals, on=['MonthNum', 'Month', 'Category'], how='left')
    filled_totals['Cost'] = filled_totals['Cost'].fillna(0)

    # Step 4: Sort by MonthNum for time order
    filled_totals = filled_totals.sort_values('MonthNum')

    # Step 5: Plot
    if category_colors is None:
        fig = px.line(
            filled_totals, x='Month', y='Cost',
            color='Category', markers=True,
            title=f'Monthly Spending by Category ({year})',
            labels={'Cost': 'Total Cost ($)', 'Month': 'Month'}
        )
    else:
        fig = px.line(
            filled_totals, x='Month', y='Cost',
            color='Category', markers=True,
            title=f'Monthly Spending by Category ({year})',
            labels={'Cost': 'Total Cost ($)', 'Month': 'Month'},
            color_discrete_map=category_colors
        )

    return fig

def plot_monthly_spending_bars_by_category(df: pd.DataFrame, year: int, category_colors=None):
    # Step 1: Create full Month + Category grid
    df_year = df[df['Year'] == year]
    # Group by MonthNum, Month, and Category
    monthly_category_totals = df_year.groupby(['MonthNum', 'Month', 'Category'], sort=False)['Cost'].sum().reset_index()

    # Sort by MonthNum for correct time order
    monthly_category_totals = monthly_category_totals.sort_values('MonthNum')

    # Plot
    if category_colors is not None:
        fig = px.bar(
            monthly_category_totals, x='Month', y='Cost',
            color='Category', title=f'Monthly Spending by Category ({year})',
            labels={'Cost': 'Total Cost ($)', 'Month': 'Month'},
            color_discrete_map=category_colors,
            barmode='group'
        )
    else:
        fig = px.bar(
            monthly_category_totals, x='Month', y='Cost',
            color='Category', title=f'Monthly Spending by Category ({year})',
            labels={'Cost': 'Total Cost ($)', 'Month': 'Month'},
            barmode='group'
        )
    
    return fig

def plot_annual_spending_pie_by_category(df: pd.DataFrame, year: int, category_colors=None):
    # Step 1: Create full Month + Category grid
    df_year = df[df['Year'] == year]
    # Group data by Category and sum the costs
    category_totals = df_year.groupby('Category')['Cost'].sum().reset_index()

    # Create a pie chart
    if category_colors is not None:
        fig = px.pie(
            category_totals,
            names='Category', values='Cost', color="Category",
            title=f'Monthly Spending by Category ({year})',
            color_discrete_map=category_colors
        )
    else:
        fig = px.pie(
            category_totals,
            names='Category', values='Cost', color="Category",
            title=f'Monthly Spending by Category ({year})',
        )

    return fig

def plot_avg_spend_per_item(df: pd.DataFrame, year: int, category_colors=None):
    df_year = df[df['Year'] == year]

    avg_spend = df_year.groupby('Category').agg(
        Avg_Spend_Per_Item=('Cost', 'mean'),
        Total_Items=('Item', 'count'),
        Total_Spent=('Cost', 'sum')
    ).sort_values("Avg_Spend_Per_Item").reset_index()

    fig = px.bar(
        avg_spend,
        y='Category',
        x='Avg_Spend_Per_Item',
        text='Avg_Spend_Per_Item',
        hover_data=['Total_Items', 'Total_Spent'],
        title=f'Average Spend per Item by Category ({year})',
        labels={'Avg_Spend_Per_Item': 'Avg Spend ($)', 'Category': 'Category'},
        orientation='h'
    )

    if category_colors is not None:
        fig.update_traces(marker_color=avg_spend['Category'].map(category_colors))

    fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    fig.update_layout(yaxis_tickprefix='', uniformtext_minsize=8, uniformtext_mode='hide')

    return fig

def plot_top_items_in_category(df: pd.DataFrame, year: int, top_n: int = 10):
    df_year = df[df['Year'] == year]
    top_items = df_year.sort_values(by="Cost", ascending=False).head(top_n).reset_index(drop=True)

    fig = px.bar(
        top_items,
        x='Cost',
        y='Item',
        orientation='h',
        title='Top Items by Cost',
        labels={'Cost': 'Cost ($)', 'Item': 'Item'},
        text='Cost'
    )
    fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    fig.update_layout(xaxis_tickprefix='$', yaxis=dict(autorange="reversed"))

    return fig

def plot_monthly_spending_in_category(df: pd.DataFrame, year: int):
    df_year = df[df['Year'] == year]
    cat_monthly = df_year.groupby(['MonthNum', 'Month'])['Cost'].sum().reset_index()
    cat_monthly = cat_monthly.sort_values('MonthNum').reset_index(drop=True)

    fig = px.bar(
        cat_monthly,
        x='Month',
        y='Cost',
        title='Monthly Spending',
        labels={'Cost': 'Total Cost ($)', 'Month': 'Month'},
        text='Cost'
    )
    fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    fig.update_layout(yaxis_tickprefix='$')

    return fig


def plot_annual_spending_by_category(df: pd.DataFrame, category_colors=None):
    # Make sure Year is string so it's categorical
    df['Year'] = df['Year'].astype(str)

    # Group totals
    category_year_totals = df.groupby(['Year', 'Category'])['Cost'].sum().reset_index()

    # Plot: X = Year, color = Category
    if category_colors is not None:
        fig = px.bar(
            category_year_totals,
            x='Year', y='Cost',
            color='Category', barmode='group', 
            title='Total Spending by Year (Grouped by Category)',
            labels={'Cost': 'Total Cost ($)', 'Year': 'Year'},
            color_discrete_map=category_colors,  # Use the custom color map
        )
    else:
        fig = px.bar(
            category_year_totals,
            x='Year', y='Cost',
            color='Category', barmode='group', 
            title='Total Spending by Year (Grouped by Category)',
            labels={'Cost': 'Total Cost ($)', 'Year': 'Year'}
        )

    return fig

def plot_monthly_spending_trends_by_year(df: pd.DataFrame):
    # Step 1: Create full Month + Year grid
    all_months = df[['MonthNum', 'Month']].drop_duplicates()
    all_years = df['Year'].drop_duplicates()
    month_year_grid = all_months.merge(all_years, how='cross')

    # Step 2: Actual totals per Year and Month
    yearly_totals = df.groupby(['MonthNum', 'Month', 'Year'])['Cost'].sum().reset_index()

    # Step 3: Merge and fill missing months with 0
    filled_yearly_totals = month_year_grid.merge(yearly_totals, on=['MonthNum', 'Month', 'Year'], how='left')
    filled_yearly_totals['Cost'] = filled_yearly_totals['Cost'].fillna(0)

    # Step 4: Sort for correct time order
    filled_yearly_totals = filled_yearly_totals.sort_values(['Year', 'MonthNum'])

    # Step 5: Plot
    fig = px.line(
        filled_yearly_totals, x='Month', y='Cost',
        color='Year', markers=True,
        title='Monthly Spending by Year',
        labels={'Cost': 'Total Cost ($)', 'Month': 'Month'},
    )

    return fig


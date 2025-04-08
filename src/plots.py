import plotly.express as px
import pandas as pd

def plot_yearly_line(df: pd.DataFrame, year: int, category_colors=None):
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

def plot_yearly_bar(df: pd.DataFrame, year: int, category_colors=None):
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
            barmode='stack'
        )
    else:
        fig = px.bar(
            monthly_category_totals, x='Month', y='Cost',
            color='Category', title=f'Monthly Spending by Category ({year})',
            labels={'Cost': 'Total Cost ($)', 'Month': 'Month'},
            barmode='stack'
        )
    
    return fig

def plot_yearly_pie(df: pd.DataFrame, year: int, category_colors=None):
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

def plot_comparison_line(df: pd.DataFrame):
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

def plot_comparison_bar(df: pd.DataFrame, category_colors=None):
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
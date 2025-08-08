import plotly.express as px
import pandas as pd

def plot_spend_trend_line_month_and_category(
        df: pd.DataFrame,
        category_colors: dict | None = None,
        category: bool = False
    ):
    """Plot monthly spending.

    Parameters
    ----------
    df : DataFrame
        Needs columns 'Date', 'Cost', and (if category=True) 'Category'.
    category_colors : dict, optional
        Mapping {category: colour}. Used only when category=True.
    category : bool, default False
        False → single aggregate line; True → separate line per category.
    """
    df = df.copy()

    # 1️⃣ Ensure date column and derive month order + label
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)

    bad_dates = df[df["Date"].isna()]
    if not bad_dates.empty:
        print("⚠️ Rows with invalid or unrecognized date formats:")
        print("Excel Rows:", bad_dates.index + 2)
        print(bad_dates[["Item", "Date"]])

    df["MonthNum"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    df["Month"] = df["MonthNum"].dt.strftime("%Y-%m")
    df["MonthNum"] = df["MonthNum"].fillna(pd.NaT)
    df["Month"] = df["Month"].fillna("Unknown")

    # 2️⃣ Build full grid
    months = df[["MonthNum", "Month"]].drop_duplicates()
    if category:
        cats = df["Category"].drop_duplicates()
        full_grid = months.merge(cats, how="cross")
        totals = df.groupby(["MonthNum", "Month", "Category"], as_index=False)["Cost"].sum()
        filled = (
            full_grid.merge(totals, on=["MonthNum", "Month", "Category"], how="left")
                     .fillna({"Cost": 0})
                     .sort_values("MonthNum")
        )
    else:
        full_grid = months
        totals = df.groupby(["MonthNum", "Month"], as_index=False)["Cost"].sum()
        filled = (
            full_grid.merge(totals, on=["MonthNum", "Month"], how="left")
                     .fillna({"Cost": 0})
                     .sort_values("MonthNum")
        )

    # 3️⃣ Plot
    base_kwargs = dict(
        x="Month",
        y="Cost",
        markers=True,
        labels={"Cost": "Total Cost ($)", "Month": "Month"},
    )

    if category:
        fig = px.line(
            filled,
            color="Category",
            title="Monthly Spending by Category",
            **base_kwargs,
            color_discrete_map=category_colors
        ) 
        # 🔹 Add category-specific average lines
        if category_colors:
            cat_avgs = (
                filled.groupby("Category", as_index=False)["Cost"]
                .mean()
                .rename(columns={"Cost": "AvgCost"})
            )

            for _, row in cat_avgs.iterrows():
                cat = row["Category"]
                avg = row["AvgCost"]
                color = category_colors.get(cat, "gray")

                fig.add_hline(
                    y=avg,
                    line_dash="dot",
                    line_color=color,
                    annotation_text=f"{cat} Avg: ${avg:,.2f}",
                    annotation_position="top left",
                    annotation_font_color=color,
                    opacity=0.6
                )
    else:
        fig = px.line(
            filled,
            title="Monthly Spending Over Time",
            text="Cost",  # 🔹 show amount at each point
            **base_kwargs
        )

        # Add average horizontal line
        avg_cost = filled["Cost"].mean()
        fig.add_hline(
            y=avg_cost,
            line_dash="dot",
            line_color="gray",
            annotation_text=f"Average: ${avg_cost:.2f}",
            annotation_position="top left"
        )
        
        # 🔹 Format point labels
        fig.update_traces(
            texttemplate="$%{text:,.2f}",
            textposition="top center",
            textfont=dict(
                color="black",  # ✅ more visible
                size=12         # optional: bump size for clarity
            )
        )

    fig.update_layout(xaxis_tickangle=-45)
    return fig


def plot_spend_trend_bars_month_and_category(df: pd.DataFrame, category_colors=None):
    # Step 1: Create full Month + Category grid
    # Group by MonthNum, Month, and Category
    monthly_category_totals = df.groupby(['MonthNum', 'Month', 'Category'], sort=False)['Cost'].sum().reset_index()

    # Sort by MonthNum for correct time order
    monthly_category_totals = monthly_category_totals.sort_values('MonthNum')

    # Plot
    if category_colors is not None:
        fig = px.bar(
            monthly_category_totals, x='Month', y='Cost',
            color='Category', title=f'Monthly Spending by Category',
            labels={'Cost': 'Total Cost ($)', 'Month': 'Month'},
            color_discrete_map=category_colors,
            barmode='group'
        )
    else:
        fig = px.bar(
            monthly_category_totals, x='Month', y='Cost',
            color='Category', title=f'Monthly Spending by Category',
            labels={'Cost': 'Total Cost ($)', 'Month': 'Month'},
            barmode='group'
        )
    
    return fig

def plot_spend_trend_line_month_and_year(df: pd.DataFrame):
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

def plot_spend_trend_line_monthly(
    df: pd.DataFrame,
    category_colors: dict | None = None,
    category: bool = False,
):
    """Return a Plotly line chart of monthly spending.

    Parameters
    ----------
    df : DataFrame
        Must contain columns 'Date', 'Cost', and (if category=True) 'Category'.
    category_colors : dict, optional
        Mapping {category_name: hex_color}. Only used when category=True.
    category : bool, default False
        If True, plot one line per category; otherwise plot the aggregate.
    """
    df = df.copy()

    # 1️⃣ Ensure datetime and Year-Month key
    df["Date"] = pd.to_datetime(df["Date"])
    df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)

    # 2️⃣ Aggregate
    if category:
        monthly = (df.groupby(["YearMonth", "Category"], as_index=False)["Cost"].sum())
    else:
        monthly = (df.groupby("YearMonth", as_index=False)["Cost"].sum())

    # 3️⃣ Build the figure
    base_kwargs = dict(
        x="YearMonth",
        y="Cost",
        markers=True,
        labels={"Cost": "Total Spend ($)", "YearMonth": "Month"},
    )

    if category:
        fig = px.line(
            monthly,
            color="Category",
            title="Monthly Spending by Category",
            **base_kwargs,
            color_discrete_map=category_colors,
        )
    else:
        fig = px.line(
            monthly,
            title="Monthly Spending Over Time",
            **base_kwargs,
        )

    fig.update_layout(xaxis_tickangle=-45)
    return fig


def plot_spending_by_category_pie(df: pd.DataFrame, category_colors=None):
    # Step 1: Create full Month + Category grid
    # Group data by Category and sum the costs
    category_totals = df.groupby('Category')['Cost'].sum().reset_index()
    title = "Total Spending by Category"

    # Create a pie chart
    if category_colors is not None:
        fig = px.pie(
            category_totals,
            names='Category', values='Cost', color="Category",
            title=title,
            color_discrete_map=category_colors
        )
    else:
        fig = px.pie(
            category_totals,
            names='Category', values='Cost', color="Category",
            title=title,
        )

    return fig

def plot_avg_spend_per_category(df: pd.DataFrame, category_colors=None):

    avg_spend = df.groupby('Category').agg(
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
        title=f'Average Spend per Item by Category',
        labels={'Avg_Spend_Per_Item': 'Avg Spend ($)', 'Category': 'Category'},
        orientation='h'
    )

    if category_colors is not None:
        fig.update_traces(marker_color=avg_spend['Category'].map(category_colors))

    fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    fig.update_layout(yaxis_tickprefix='', uniformtext_minsize=8, uniformtext_mode='hide')

    return fig

def plot_top_items_in_category(df: pd.DataFrame, top_n: int = 10):
    top_items = df.sort_values(by="Cost", ascending=False).head(top_n).reset_index(drop=True)

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

def plot_monthly_spending_in_category(df: pd.DataFrame):
    cat_monthly = df.groupby(['MonthNum', 'Month'])['Cost'].sum().reset_index()
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

def plot_cost_scatter(df: pd.DataFrame):
    df = df.reset_index(drop=True)
    df['Index'] = df.index + 1

    fig = px.scatter(
        df,
        x='Index',
        y='Cost',
        title="Scatter Plot of Item Costs",
        labels={'Index': 'Purchase Order', 'Cost': 'Item Cost ($)'},
        hover_data=['Item', 'Category', 'Date'] if 'Date' in df.columns else ['Item', 'Category']
    )

    fig.update_layout(yaxis_tickprefix='$')
    # fig.update_layout(yaxis_type='log')
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


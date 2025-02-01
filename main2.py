import streamlit as st
import pandas as pd
from datetime import datetime


def main():
    folder = 'G:/My Drive/FINANCE'
    csv_file = f'{folder}/report_2024-12-23_074803.csv'
    accounts_file = f'{folder}/starting_balance.json'

    transactions_df = pd.read_csv(csv_file, sep=';')
    accounts_json = pd.read_json(accounts_file)
    accounts_df = pd.json_normalize(accounts_json['data'])
    accounts_df.columns = ['account', 'starting_balance', 'account_type', 'account_currency', 'archived']
    merged = pd.merge(transactions_df, accounts_df, on='account', how='left')
    active_transactions = merged[~merged['archived']]
    total_starting = accounts_df['starting_balance'].sum()
    running_balance_df = running_balance(active_transactions, total_starting)

    show_category_stats(active_transactions)


def running_balance(transactions, total_starting=0):
    sorted = transactions.sort_values(['date', 'category'], ascending=[True, True])
    sorted['cumulative_sum'] = sorted['amount'].cumsum()
    sorted['cumulative_sum'] = sorted['cumulative_sum'] + total_starting
    return sorted


def show_category_stats(df):
    df = df.copy()
    # with st.expander("Category Statistics", expanded=True):
    show_details = st.checkbox(label="Show details?")

    if show_details:
        colA1, colA2 = st.columns(2)
        with colA1:
            display_1(df)
        with colA2:
            st.write("A")
    else:
        display_1(df)


def display_1(df):
    with st.container(height=690):
        time_span = st.radio("Time Span", ["Overall", "Year", "Month"], 1, horizontal=True)

        if time_span == "Month":
            html_code = """
            <style>
                label, p {
                    font-family: Roboto, sans-serif;
                    color: white;
                }
                input {
                    font-family: Roboto, sans-serif;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                    border: 1px solid #4CAF50;
                    padding: 8px;
                }
            </style>
            <div>
                <label for="month">Select a month:</label>
                <input type="month" id="month" name="month" onchange="handleMonthChange(event)">
                <p id="output">Selected Month: None</p>
            </div>
            <script>
                function handleMonthChange(event) {
                    const selectedMonth = event.target.value;
                    document.getElementById('output').textContent = 'Selected Month: ' + selectedMonth;
                }
            </script>
            """
            st.components.v1.html(html_code, height=150)
        elif time_span == "Year":
            current_year = datetime.now().year
            years = [year for year in range(current_year, current_year - 3, -1)]
            selected_year = st.selectbox("Year", years)
            df['date'] = pd.to_datetime(df['date'])
            filtered_df = df[df['date'].dt.year == selected_year]
        elif time_span == "Overall":
            filtered_df = df
        
        filtered_df = filtered_df[filtered_df["category"] != "TRANSFER"]

        st.title("Total")
        st.dataframe([{
                "Category": "Total",
                "Count": filtered_df["amount"].count(),
                "Sum": filtered_df["amount"].sum(),
            }], use_container_width=True
        )


        colB1, colB2, colB3 = st.columns((6,2,3))
        with colB1:
            st.title("Inflow / Outflow")
        with colB2:
            io_details = st.checkbox("Show details")
        with colB3:
            io_select = st.selectbox("Select:", ["Expenses", "Income"])

        st.dataframe(
            filtered_df[["type", "amount"]].groupby("type").agg(
                Count=("type", "count"),
                Sum=("amount", "sum"),
            ), use_container_width=True
        )
    

        st.title("Category Statistics")
        category_df = filtered_df[["category", "amount"]].groupby("category").agg(
            Count=("category", "count"),
            Sum=("amount", "sum"),
        ).sort_values(by=["Sum"])
        with st.container(border=True, height=500):
            for key, row in category_df.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.button(key)
                with col2:
                    st.text(int(round(row["Count"], 0)))
                    # print(row["Count"])
                with col3:
                    st.text(round(row["Sum"], 2))
        # st.dataframe(
        #     category_df,
        #     use_container_width=True
        # )

        # selected_row = st.data_editor(category_df, use_container_width=True, key="category")
        # if selected_row is not None:
        #     st.write(selected_row)

        st.title("Monthly Expenses")
        filtered_df["month"] = filtered_df["date"].dt.month
        expenses_df = filtered_df[filtered_df["type"] == "Expenses"]
        st.dataframe(
            expenses_df[["month", "amount"]].groupby("month").agg(
                Count=("month", "count"),
                Sum=("amount", "sum"),
            ), use_container_width=True
        )

        st.title("Data")
        st.dataframe(
            filtered_df[["account", "category", "amount", "note", "date", "labels"]],
            use_container_width=True
        )


if __name__ == '__main__':
    main()
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import plotly.graph_objects as go
import streamlit as st


def main():
    folder = '.'
    csv_file = f'{folder}/report_2024-10-18_211441.csv'
    accounts_file = f'{folder}/starting_balance.json'

    transactions_df = pd.read_csv(csv_file, sep=';')
    accounts_json = pd.read_json(accounts_file)
    accounts_df = pd.json_normalize(accounts_json['data'])
    accounts_df.columns = ['account', 'starting_balance', 'account_type', 'account_currency', 'archived']
    merged = pd.merge(transactions_df, accounts_df, on='account', how='left')
    active_transactions = merged[~merged['archived']]
    total_starting = accounts_df['starting_balance'].sum()
    running_balance_df = running_balance(active_transactions, total_starting)

    # print_details(details={
    #     "total_starting": total_starting,
    #     "accounts_df": accounts_df,
    #     "transactions_df": transactions_df,
    #     "accounts_json": accounts_json,
    #     "running_balance_df": running_balance_df,
    # })
    create_sidebar()
    plot_ohlc(running_balance_df)
    tabular_df = running_balance_df[['account', 'category', 'amount', 'date', 'cumulative_sum']].copy()
    st.dataframe(tabular_df, use_container_width=True)
    # st.dataframe(active_transactions[["category", "amount"]].groupby("category").count(), use_container_width=True)
    st.dataframe(
        active_transactions[["category", "amount"]].groupby("category").agg(
            Count=("category", "count"),
            Sum=("amount", "sum"),
        ), use_container_width=True
    )
    # cols1 = st.columns(2)
    # for col in cols1:
    #     with col:
    #         st.write('this is a column')
    show_month_detail(active_transactions)


def create_sidebar():
    st.sidebar.title("Financial Analysis")
    with st.sidebar.expander("Expander 1"):
        st.caption("Some contents")

def describe_data(data):
    print('*' * 60, 'HEAD',  '*' * 60)
    print(data.head())
    print('*' * 60, 'SHAPE',  '*' * 60)
    print(data.shape)
    print('*' * 60, 'INFO',  '*' * 60)
    print(data.info())


def account_summary(transactions, accounts):
    total = transactions.groupby(['account'])['amount'].agg(['sum', 'count'])
    additional_df = pd.DataFrame(
        [(acc['account'], acc['starting_balance']) for acc in accounts['data']],
        columns=['account', 'starting_balance']
    )
    additional_df.set_index('account', inplace=True)
    merged_df = total.merge(additional_df, left_index=True, right_index=True, how='left')
    merged_df['total'] = merged_df['sum'] + merged_df['starting_balance']
    return merged_df


def running_balance(transactions, total_starting=0):
    # total_by_date_account_category = transactions.groupby(['date', 'account', 'category'])['amount'].agg(['sum', 'count'])
    # return total_by_date_account_category
    sorted = transactions.sort_values(['date', 'category'], ascending=[True, True])
    sorted['cumulative_sum'] = sorted['amount'].cumsum()
    sorted['cumulative_sum'] = sorted['cumulative_sum'] + total_starting
    return sorted


def plot_running_balance(df):
    df['date_only'] = pd.to_datetime(df['date']).dt.date
    daily_total = df.groupby('date_only')['cumulative_sum'].last()
    print(daily_total)
    plt.figure(figsize=(20, 10))
    daily_total.plot(kind='line', marker='o')
    plt.title('Cumulative Total by Date')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.show()


def print_details(details):
    print(f'TOTAL STARTING BALANCE: {details["total_starting"]}')
    print('\n', '-' * 50, 'ACCOUNT DETAILS', '-' * 50)
    print(details["accounts_df"][details["accounts_df"]['starting_balance'] > 0].sort_values(by='starting_balance', ascending=False))
    print('\n', '-' * 50, 'ACCOUNT SUMMARY', '-' * 50)
    # describe_data(transactions_df)
    # describe_data(merged)
    print(account_summary(details["transactions_df"], details["accounts_json"]))
    print('\n', '-' * 50, 'RUNNING BALANCE', '-' * 50)
    print(details["running_balance_df"])
    print(details["running_balance_df"].info())
    

def plot_ohlc(df):
    df['date'] = pd.to_datetime(df['date'])
    df['day'] = df['date'].dt.date
    df['year'] = df['date'].dt.isocalendar().year
    df['week'] = df['date'].dt.isocalendar().week
    df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.weekday, unit='D')
    df['week_start'] = df['week_start'].dt.date
    df['month_year'] = df['date'].apply(lambda x: x.strftime('%B-%Y'))

    
    with st.container(border=True):
        col1, col2 = st.columns([1, 1])
        with col1:
            chart_type = st.radio("Chart Type", ["Line", "Candlestick"], horizontal=True)
            date_span = st.radio("Date Span", ["Day", "Week", "Month"], 1, horizontal=True)
        
        date_span_dict = {"Day": "day", "Week": "week_start", "Month": "month_year"}
        ohlc = df.groupby(date_span_dict[date_span]).agg(
            Open=('cumulative_sum', 'first'),
            High=('cumulative_sum', 'max'),
            Low=('cumulative_sum', 'min'),
            Close=('cumulative_sum', 'last'),
        )
        change = round(ohlc["Close"].iloc[-1] - ohlc["Close"].iloc[0], 2)
        percent_change = round(100 * change / ohlc["Close"].iloc[0], 2)
        
        min_row = df.loc[df["cumulative_sum"].idxmin()]
        max_row = df.loc[df["cumulative_sum"].idxmax()]
        min_value = round(min_row["cumulative_sum"], 2)
        max_value = round(max_row["cumulative_sum"], 2)
        with col2:
            with st.container(border=True):
                st.write(f"Variance: {change:,} [:arrow_{"up" if change > 0 else "down"}_small: {percent_change} %]")
                st.write(f"Min (All-time): {min_value:,} [{min_row[date_span_dict[date_span]]}]")
                st.write(f"Max (All-time): {max_value:,} [{max_row[date_span_dict[date_span]]}]")

        candlestick = go.Candlestick(
            x=ohlc.index,
            open=ohlc['Open'],
            high=ohlc['High'],
            low=ohlc['Low'],
            close=ohlc['Close'],
            name="ohlc",
            whiskerwidth=0.5,
            line_width=0.4,
            hoverlabel_font_size=15,
        )
        line = go.Scatter(
            x=ohlc.index,
            y=ohlc["Close"],
            mode="lines",
            # line=dict(width=1),
            line_shape="spline",
            marker=dict(size=4, symbol="circle"),
        )
        chart_to_show = candlestick if chart_type == "Candlestick" else line
        fig = go.Figure(data=[chart_to_show])

        fig.update_layout(
            title=f'Running Balance  |  {chart_type}',
            xaxis_title='Date',
            yaxis_title='Balance',
            showlegend=False,
        )

        st.plotly_chart(fig)


def recurring_df(df, group_list):
    return (df[group_list].groupby(group_list).size().reset_index(name="count").query("count >= 2"))


def show_month_detail(df):
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values("date")
    df['year_month_label'] = df['date'].apply(lambda x: x.strftime('%B %Y'))
    df['time'] = df['date'].apply(lambda x: x.strftime('%H:%M'))
    with st.container(border=True):
        month = st.selectbox("Month", df["year_month_label"].unique())
        tabular_df = (df
            [["time", "account", "category", "amount", "note", "labels"]]
            [df["year_month_label"]==month]
            .sort_values("time")
        )
        st.dataframe(tabular_df, use_container_width=True)
        st.write(f"Total rows: {tabular_df.count()}")
        st.title("Recurring")
        group_lists = [
            ["category", "account", "note", "labels"],
            ["category", "note", "labels"],
            ["category", "account", "labels"],
            ["category", "labels"],
            ["category"],
        ]
        for i, category_list in enumerate(group_lists, start=1):
            new_df = recurring_df(df, category_list)
            st.subheader(f"{i}. {", ".join(category_list)} [count={new_df.shape[0]}]")
            st.dataframe(new_df, use_container_width=True)
            st.divider()

        # df1 = recurring_df(df, ["category", "account", "note", "labels"])
        # st.subheader(f"1. account, category, note, labels [count={df1.shape[0]}]")
        # st.dataframe(df1, use_container_width=True)
        # df2 = (df[["category", "note", "labels"]]
        #         .groupby(["category", "note", "labels"])
        #         .size()
        #         .reset_index(name='count')
        #         .query('count >= 2'))
        # st.subheader("2a. category, note, labels")
        # st.dataframe(df2, use_container_width=True)
        # st.subheader("2b. account, category, labels")
        # st.dataframe(
        #     df[["category", "account", "labels"]]
        #         .groupby(["category", "account", "labels"])
        #         .size()
        #         .reset_index(name='count')
        #         .query('count >= 2'),
        #     use_container_width=True
        # )
        # st.subheader("3. category, labels")
        # st.dataframe(
        #     df[["category", "labels"]]
        #         .groupby(["category", "labels"])
        #         .size()
        #         .reset_index(name='count')
        #         .query('count >= 2'),
        #     use_container_width=True
        # )
        # st.subheader("4. category")
        # st.dataframe(
        #     df[["category"]]
        #         .groupby(["category"])
        #         .size()
        #         .reset_index(name='count')
        #         .query('count >= 2'),
        #     use_container_width=True
        # )


if __name__ == '__main__':
    main()

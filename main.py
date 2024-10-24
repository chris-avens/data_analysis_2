import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import plotly.graph_objects as go
import streamlit as st


def main():
    folder = 'G:/My Drive/FINANCE'
    csv_file = f'{folder}/report_2024-10-18_211441.csv'
    accounts_file = f'{folder}/starting_balance.json'

    transactions_df = pd.read_csv(csv_file, sep=';')
    accounts_json = pd.read_json(accounts_file)
    accounts_df = pd.json_normalize(accounts_json['data'])
    accounts_df.columns = ['account', 'starting_balance', 'account_type', 'account_currency', 'archived']
    merged = pd.merge(transactions_df, accounts_df, on='account', how='left')
    active_transactions = merged[~merged['archived']]

    total_starting = accounts_df['starting_balance'].sum()

    print(f'TOTAL STARTING BALANCE: {total_starting}')
    print('\n', '-' * 50, 'ACCOUNT DETAILS', '-' * 50)
    print(accounts_df[accounts_df['starting_balance'] > 0].sort_values(by='starting_balance', ascending=False))
    print('\n', '-' * 50, 'ACCOUNT SUMMARY', '-' * 50)
    # describe_data(transactions_df)
    # describe_data(merged)
    print(account_summary(transactions_df, accounts_json))
    print('\n', '-' * 50, 'RUNNING BALANCE', '-' * 50)
    running_balance_df = running_balance(active_transactions, total_starting)
    print(running_balance_df)
    print(running_balance_df.info())
    # plot_running_balance(running_balance_df)
    plot_ohlc(running_balance_df)
    tabular_df = running_balance_df[['account', 'category', 'amount', 'date', 'cumulative_sum']].copy()
    st.dataframe(tabular_df)
    st.title('Table')
    st.write(tabular_df)
    cols1 = st.columns(2)
    for col in cols1:
        with col:
            st.write('this is a column')



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


def plot_ohlc(df):
    df['date'] = pd.to_datetime(df['date'])
    df['day'] = df['date'].dt.date
    df['year'] = df['date'].dt.isocalendar().year
    df['week'] = df['date'].dt.isocalendar().week
    df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.weekday, unit='D')
    df['week_start'] = df['week_start'].dt.date
    df['month_year'] = df['date'].apply(lambda x: x.strftime('%B-%Y'))

    ohlc = df.groupby('week_start').agg(
        Open=('cumulative_sum', 'first'),
        High=('cumulative_sum', 'max'),
        Low=('cumulative_sum', 'min'),
        Close=('cumulative_sum', 'last'),
    )

    # ohlc.index = pd.to_datetime(ohlc.index)

    # mpf.plot(ohlc, type='candle', style='charles', title='Running Balance', ylabel='Balance', datetime_format='%Y-%m-%d', tight_layout=True)
    fig = go.Figure(data=[go.Candlestick(
        x=ohlc.index,
        open=ohlc['Open'],
        high=ohlc['High'],
        low=ohlc['Low'],
        close=ohlc['Close'],
        # increasing_line_color='green',
        # decreasing_line_color='red',
        whiskerwidth=0.5,
        line_width=0.4,
        hoverlabel_font_size=20,
    )])

    fig.update_layout(
        title='Running Balance',
        xaxis_title='Date',
        yaxis_title='Balance',
        # xaxis_rangeslider_visible=True,
        # xaxis=dict(
        #     range=[ohlc.index.min(), ohlc.index.min() + pd.DateOffset(day=2)],
        #     rangeslider=dict(visible=True),
        #     type='date',
        #     fixedrange=False,
        # ),
        # dragmode='pan',
    )

    # fig.show()
    st.plotly_chart(fig)


if __name__ == '__main__':
    main()

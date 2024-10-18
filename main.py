import pandas as pd


def main():
    folder = '.'
    csv_file = f'{folder}/report_2024-10-18_211441.csv'
    starting_balance_file = f'{folder}/starting_balance.json'
    df = pd.read_csv(csv_file, sep=';')
    starting_balance = pd.read_json(starting_balance_file)
    # describe_data(df)
    total = df.groupby(['account'])['amount'].agg(['sum', 'count'])
    print(total, '\n', '-' * 60)
    print(starting_balance['data'], '\n', '-' * 60)
    print('Cash sum:', total.loc['Cash', 'sum'], '\n', '-' * 60)
    # for category, row in total.iterrows():
    #     print('{', f'"account": "{category}", "starting_balance": 0, "type": "cash", "currency": "PHP", "archive": false', '},')
    for account in starting_balance['data']:
        print(f'{account["account"]}: {account["starting_balance"]}')


def describe_data(data):
    print('*' * 60, 'HEAD',  '*' * 60)
    print(data.head())
    print('*' * 60, 'SHAPE',  '*' * 60)
    print(data.shape)
    print('*' * 60, 'INFO',  '*' * 60)
    print(data.info())


if __name__ == '__main__':
    main()

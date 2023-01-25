from hourly import get_main_path, get_day, get_hour, get_params_path, load_params_from_txt
import os
import pandas as pd
import datetime
from client import GraphQlClient
import luxor

if __name__ == '__main__':

    main_file_path = get_main_path()
    params_file_path = get_params_path()

    xlsx_path = os.path.join(main_file_path, 'Facturacion.xlsx')
    luxor_key_path = os.path.join(params_file_path,'luxor_key.txt')

    luxor_key = load_params_from_txt(luxor_key_path)
    method = "POST"
    host = "https://api.beta.luxor.tech/graphql"

    client  = GraphQlClient(
        host= host,
        method=method,
        key= luxor_key,
    )

    day = get_day()
    hour = get_hour()

    data = pd.read_excel(xlsx_path, sheet_name='data_diaria')

    # as it executes daily at 23:xx:xx if it is delayed and it is executed past 00:00:00 the day needs to change
    if hour[:2] != '23':
        day = (datetime.date.today()-datetime.timedelta(1)).strftime("%Y/%m/%d")

    daily_data = data[data['Day'].str.contains(day)]

    if len(daily_data) == 0:
        average_hashrate = 'No hashrate'
        usd = 0
    else:   
        average_hashrate = sum(daily_data['Hashrate'])/len(daily_data)
        usd = average_hashrate*10

    username = luxor.get_subaccounts(first=10)['data']['users']['edges'][0]['node']['username']
    daily_BTC = luxor.get_subaccount_mining_summary(username,'BTC','_1_DAY')['data']['getMiningSummary']['revenue']

    daily_values = {'Day': [day],'Average Hashrate':[average_hashrate], 'USD': [usd], 'BTC': [daily_BTC]}
    daily_values = pd.DataFrame(data= daily_values)

    with pd.ExcelWriter(xlsx_path, mode = 'a', engine="openpyxl", if_sheet_exists = 'overlay') as writer:
        daily_values.to_excel(writer, sheet_name="data_mensual", startrow=writer.sheets['data_mensual'].max_row, header = False, index=False) 

        
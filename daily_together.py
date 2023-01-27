import os
import time
from client import GraphQlClient
import luxor
import pandas as pd
from datetime import timedelta, datetime, date

def load_params_from_txt(text_path):

    text_file = open(text_path)
    text = str(text_file.readline())
    text_file.close()

    return text

def get_main_path():
    user_name = os.getlogin()
    pre_user_path = 'C:/Users'
    post_user_path = 'Documents/Intiura_Miner_App'

    return os.path.join(pre_user_path,user_name,post_user_path)

def get_params_path():
    user_name = os.getlogin()
    pre_user_path = 'C:/Users'
    post_user_path = 'Documents/Intiura_Miner_App'

    return os.path.join(pre_user_path,user_name,post_user_path, 'parametros')

def get_day():
    return time.strftime("%Y/%m/%d")

def get_hour():
    return time.strftime("%H:%M:%S")

if __name__ == '__main__':

    main_file_path = get_main_path()
    xlsx_path = os.path.join(main_file_path, 'Facturacion.xlsx')

    params_file_path = get_params_path()
    luxor_key_path = os.path.join(params_file_path,'luxor_key.txt')

    min_pentahashes_path = os.path.join(params_file_path,'min_pentahashes.txt')
    min_pentahashes = float(load_params_from_txt(min_pentahashes_path))

    luxor_key = load_params_from_txt(luxor_key_path)
    method = "POST"
    host = "https://api.beta.luxor.tech/graphql"

    client  = GraphQlClient(
            host= host,
            method=method,
            key= luxor_key,
        )

    username = luxor.get_subaccounts(first=10)['data']['users']['edges'][0]['node']['username']

    values = []
    for node in luxor.get_subaccount_hashrate_history(username, 'BTC', '_1_HOUR', 25 )['data']['getHashrateHistory']['edges']:
        values.append([node['node']['time'].split('T')[0].replace('-','/'),node['node']['time'].split('T')[1].split('+')[0], float(node['node']['hashrate'])/10**15])

    values = sorted(values)

    data = pd.read_excel(xlsx_path, sheet_name='data_diaria_bruta')
    last_data_day = list(data['Day'])[-1]
    last_data_hour = list(data['Hour'])[-1]
    last_data_time = datetime(int(last_data_day[:4]), int(last_data_day[5:7]), int(last_data_day[8:]), int(last_data_hour[:2]), int(last_data_hour[3:5]), int(last_data_hour[6:]))
    
    for value in values:
        data_time = datetime(int(value[0][:4]), int(value[0][5:7]), int(value[0][8:]), int(value[1][:2]), int(value[1][3:5]), int(value[1][6:]))
        if data_time >= last_data_time:
            break
    
    values = values[values.index(value):]

    day_data_raw = [value[0] for value in values]
    hour_data_raw = [value[1] for value in values]
    hash_data_raw = [value[2] for value in values]

    day_data = [value[0] for value in values if value[2]>=min_pentahashes]
    hour_data = [value[1] for value in values if value[2]>=min_pentahashes]
    hash_data = [value[2] for value in values if value[2]>=min_pentahashes]

    values_raw = {'Day': day_data_raw,'Hour':hour_data_raw,'Hashrate':hash_data_raw}
    values = {'Day': day_data,'Hour':hour_data,'Hashrate':hash_data}

    values_raw = pd.DataFrame(data = values_raw)
    values = pd.DataFrame(data = values)

    with pd.ExcelWriter(xlsx_path, mode = 'a', engine="openpyxl", if_sheet_exists = 'overlay') as writer:
        values.to_excel(writer, sheet_name="data_diaria", startrow=writer.sheets['data_diaria'].max_row, header = False, index=False) 

    with pd.ExcelWriter(xlsx_path, mode = 'a', engine="openpyxl", if_sheet_exists = 'overlay') as writer:
        values_raw.to_excel(writer, sheet_name="data_diaria_bruta", startrow=writer.sheets['data_diaria_bruta'].max_row, header = False, index=False)

    # Calculate yesterdays values
    day = (date.today()-timedelta(1)).strftime("%Y/%m/%d")
    data = pd.read_excel(xlsx_path, sheet_name='data_diaria')
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
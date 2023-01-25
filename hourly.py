from client import GraphQlClient
import luxor
import pandas as pd
import time
import os

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

    # Parameters for the luxor API
    luxor_key = load_params_from_txt(luxor_key_path)
    min_pentahashes = float(load_params_from_txt(min_pentahashes_path))

    method = "POST"
    host = "https://api.beta.luxor.tech/graphql"

    client  = GraphQlClient(
        host= host,
        method=method,
        key= luxor_key,
    )

    username = luxor.get_subaccounts(first=10)['data']['users']['edges'][0]['node']['username']

    # Values for the excel file
    summary = luxor.get_subaccount_mining_summary(username,'BTC','_1_HOUR')['data']['getMiningSummary']
    summary_values = [float(info) for info in list(summary.values())]
    pentahashes = summary_values[0] / 10**15
    day = get_day()
    hour = get_hour()
    summary_values = {'Day': [day],'Hour':[hour],'Hashrate':[pentahashes]}

    summary_values = pd.DataFrame(data = summary_values)

    # Writing on Excel the hourly data if the hasrate is more than 25 pentahashes

    if pentahashes >= min_pentahashes:
        with pd.ExcelWriter(xlsx_path, mode = 'a', engine="openpyxl", if_sheet_exists = 'overlay') as writer:
            summary_values.to_excel(writer, sheet_name="data_diaria", startrow=writer.sheets['data_diaria'].max_row, header = False, index=False) 

    with pd.ExcelWriter(xlsx_path, mode = 'a', engine="openpyxl", if_sheet_exists = 'overlay') as writer:
        summary_values.to_excel(writer, sheet_name="data_diaria_bruta", startrow=writer.sheets['data_diaria'].max_row, header = False, index=False)
from client import GraphQlClient
import luxor
from csv import writer
import time
import os

def load_params_from_txt(text_path):

    text_file = open(text_path)
    text = str(text_file.readline())
    text_file.close()

    return text

if __name__ == '__main__':

    # Declaring the main ant the params path
    user_name = os.getlogin()
    pre_user_path = 'C:/Users'
    post_user_path = 'Documents/Intiura_Miner_App'
    main_file_path = os.path.join(pre_user_path,user_name,post_user_path)
    params_file_path = os.path.join(pre_user_path,user_name,post_user_path, 'parametros')

    # Declaring other paths
    luxor_key_path = os.path.join(params_file_path,'luxor_key.txt')
    csv_path = os.path.join(main_file_path, 'miners_data_hour.csv')

    luxor_key = load_params_from_txt(luxor_key_path)
    method = "POST"
    host = "https://api.beta.luxor.tech/graphql"

    client  = GraphQlClient(
        host= host,
        method=method,
        key= luxor_key,
    )

    
    # luxor.get_subaccounts(first=10)
    username = luxor.get_subaccounts(first=10)['data']['users']['edges'][0]['node']['username']

    # C:\Users\ikerm\Documents\python_resources\luxor_api\ps_script.ps1
    # mpn: mining profile name
    # org_slug: organization name
    # cid (str): Currency identifier, refers to the coin ticker; e.g. BTC

    
    summary = luxor.get_subaccount_mining_summary(username,'BTC','_1_HOUR')['data']['getMiningSummary']
    summary_values = [float(info) for info in list(summary.values())]
    summary_values[0] /= 10**15
    day = time.strftime("%Y/%m/%d,%H:%M:%S").split(',')[0]
    hour = time.strftime("%Y/%m/%d,%H:%M:%S").split(',')[1]
    summary_values.insert(0,hour)
    summary_values.insert(0,day)

    # Open our existing CSV file in append mode
    # Create a file object for this file
    with open(csv_path, 'a',newline='') as f_object:
    
        # Pass this file object to csv.writer()
        # and get a writer object
        writer_object = writer(f_object)
    
        # Pass the list as an argument into
        # the writerow()
        writer_object.writerow(summary_values)
    
        # Close the file object
        f_object.close()

    # subaccount: ikerinti,
    # mpn: BTC,
    # input_interval: _15_MINUTE, _1_HOUR, _1_HOUR and _1_DAY
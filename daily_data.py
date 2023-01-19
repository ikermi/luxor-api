import os
import pandas as pd
import time
from csv import writer

def read_daily_data(input_path, day):

    data = pd.read_csv(input_path)


    data = data[data['Day'].str.contains(day)]

    return data

def get_and_write_daily_status(daily_data, csv_path, day):
    
    status_list = [day]

    average_hashrate = sum(daily_data['Hashrate'])/len(daily_data)
    status_list.append(average_hashrate)

    average_bill = average_hashrate*10
    status_list.append(average_bill)

    with open(csv_path, 'a',newline='') as f_object:
    
        # Pass this file object to csv.writer()
        # and get a writer object
        writer_object = writer(f_object)
    
        # Pass the list as an argument into
        # the writerow()
        writer_object.writerow(status_list)
    
        # Close the file object
        f_object.close()


def write_month_bill(csv_month):

    month_bil = []

    with open(csv_month, 'a',newline='') as f_object:
    
        # Pass this file object to csv.writer()
        # and get a writer object
        writer_object = writer(f_object)
    
        # Pass the list as an argument into
        # the writerow()
        writer_object.writerow(month_bil)
    
        # Close the file object
        f_object.close()

    return False

if __name__ == '__main__':

    # Ejecutar a las 23:00

    user_name = os.getlogin()
    pre_user_path = 'C:/Users'
    post_user_path = 'Documents/Intiura_Miner_App'
    
    csv_path_daily_data = os.path.join(pre_user_path, user_name, post_user_path, 'miners_data_hour.csv')
    csv_bill = os.path.join(pre_user_path, user_name, post_user_path, 'miners_daily.csv')
    csv_month = os.path.join(pre_user_path, user_name, post_user_path, 'month_bill.csv')

    day = time.strftime("%Y/%m/%d")

    daily_data = read_daily_data(csv_path_daily_data, day)

    get_and_write_daily_status(daily_data, csv_bill, day)

    day_timestamp = pd.Timestamp(int(day.split('/')[0]), int(day.split('/')[1]), int(day.split('/')[2]))

    if day_timestamp.is_month_end == True:
        write_month_bill()

    print('')
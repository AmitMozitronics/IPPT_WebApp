import pandas as pd
from datetime import datetime
def calculate_downtime(df):
    df['Pipe Type'] = df['basic_metarial'].astype(str)  + " " + df['standard_type_classification'].astype(str) + " " +  df['pressure_type_specification'].astype(str)
    unique_pipe_type = df['Pipe Type'].unique()
    d_time=0
    for pipe in unique_pipe_type:
        df_pipe_wise = df.loc[df["Pipe Type"]==pipe]
        x=generic_downtime(df_pipe_wise)
        print("pipe --{} downtime is {}".format(pipe, x))
        d_time += x
    return d_time

def generic_downtime(df):
    datetime_data = pd.to_datetime(df['site_local_time'])
    datetime_data_no_timezone = []
    for i in datetime_data:
        d = i.replace(tzinfo = None)
        datetime_data_no_timezone.append(d)
    print(datetime_data_no_timezone[0])
    df['processed_datetime']=pd.to_datetime(datetime_data_no_timezone)
    x=df['processed_datetime']
    frmt = '%Y-%m-%d %H:%M:%S'

    diff=datetime.strptime(str(df.iloc[0]['processed_datetime']), frmt)-datetime.strptime(str(df.iloc[1]['processed_datetime']), frmt)
    total_entries = int(len(df.index))

    diff_time=[]
    frmt = '%Y-%m-%d %H:%M:%S'
    for i in range(total_entries-1):
        x=datetime.strptime(str(df.iloc[i]['processed_datetime']), frmt)-datetime.strptime(str(df.iloc[i+1]['processed_datetime']), frmt)
        x_sec = x.total_seconds()
        diff_time.append(x_sec)

    diff_time.sort()
    delta_dic={}
    for i in range(len(diff_time)):
        if diff_time[i] not in delta_dic.keys():
            delta_dic[diff_time[i]] = 1
        else:
            delta_dic[diff_time[i]] += 1

    a = [i for i in delta_dic.values()]
    max_ocurance_value = max(a)

    x_data = list(delta_dic.keys())
    y_data = list(delta_dic.values())
    dict(list(delta_dic.items())[:10])

    band=[]
    for i in range(10, len(delta_dic), 10):
        band_of_ten = dict(list(delta_dic.items())[i-10:i])
        band.append(band_of_ten)
    band.append(dict(list(delta_dic.items())[i:len(delta_dic)]))

    k=1
    sample_frq = -111
    for element in band:
        each_band_frq = 0
        for value in element.values():
            each_band_frq = each_band_frq + value
        element['band_frq'] = each_band_frq
        if each_band_frq>sample_frq:
            max_frq = each_band_frq
            sample_frq = each_band_frq
            max_band_index = band.index(element)

    max_band = band[max_band_index]
    
    del max_band['band_frq']
    max_band_sorted_value = sorted(max_band.values())
    max_timedelta_frq_max_band = max_band_sorted_value[9]

    max_occurence_timedifference = None
    for key, value in max_band.items():
        if value == max_timedelta_frq_max_band:
            max_occurence_timedifference = key

    downtime = 0
    for i in diff_time:
        if i > max_occurence_timedifference:
            downtime+= (i - max_occurence_timedifference)
    total_downtime = downtime/3600
    return total_downtime

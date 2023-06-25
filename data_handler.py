import pandas as pd


def add_sheet_to_xls(xls_filename, csv_filenames):
    writer = pd.ExcelWriter(xls_filename, engine='xlsxwriter')
    for csv_filename in csv_filenames:
        df = pd.read_csv(csv_filename)
        df.to_excel(writer, sheet_name=csv_filename.split('.')[0])
    writer.save()


def dict_to_df(dictionary):
    return pd.DataFrame.from_dict(dictionary)


def write_csv(csv_filename, dict_arr):
    data_frame = dict_to_df(dict_arr)
    data_frame.to_csv(csv_filename, encoding='utf-8-sig')




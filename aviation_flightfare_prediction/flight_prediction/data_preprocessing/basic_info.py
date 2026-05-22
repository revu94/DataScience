import pandas as pd


def read_excel_data(path:str):
    return pd.read_excel(path)

def data_info(df:pd.DataFrame):
    print(df.info(),"\n")

def column_unique_values(col:pd.DataFrame)->str:
    return f"The unique values for {col} are \n {col.value_counts()}"


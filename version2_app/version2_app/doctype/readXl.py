from os import PRIO_USER
import pandas as pd
from pandas.core.indexes.base import Index
import numpy as np
file_name_d140 = '/home/caratred/Desktop/gst_configdata/JWMarriottAerocity/D140 1st Nov21.xlsx' 
df_d140_read = pd.read_excel(file_name_d140, index_col=None)
df = pd.DataFrame({
    'ROOM': df_d140_read['ROOM'],
    'GUEST_FULL_NAME':df_d140_read['GUEST_FULL_NAME'],
    'TRX_DESC':df_d140_read['TRX_DESC'],
    'BUSINESS_DATE':df_d140_read['BUSINESS_DATE'],
    'CASHIER_DEBIT':df_d140_read['CASHIER_DEBIT'],
    'CASHIER_CREDIT':df_d140_read['CASHIER_DEBIT'],
    'CREDIT_CARD_SUPPLEMENT':df_d140_read['CREDIT_CARD_SUPPLEMENT'] 
}).dropna()
df['ROOM'] = df['ROOM'].replace('AR',0)
df["GUEST_FULL_NAME"] = df["GUEST_FULL_NAME"].replace(',MR|,MS|,Mr|,Ms|,ms|,mr|mr|ms|MR|MS|Ms|Mr','', regex=True)
df = df.astype({"ROOM": int})
file_name_d110 = "/home/caratred/Desktop/gst_configdata/JWMarriottAerocity/D110 1st Nov'21.xlsx"
df_d110_read = pd.read_excel(file_name_d110, index_col=None)
df_d110 = pd.DataFrame(df_d110_read, columns= ['ROOM','DISPLAY_NAME','FOLIO_TYPE','BILL_NO','BILL_GENERATION_DATE']).dropna()
df_d110 = df_d110.astype({"ROOM": int, "DISPLAY_NAME": str})
pd_merge = pd.concat([df_d110,df],join="inner",axis=1)
pd_merge.drop(['DISPLAY_NAME'],axis='columns', inplace=True)
pd_merge.to_excel("outpt.xlsx",index=False) 
# file_name_gstr4a = '/home/caratred/Desktop/gst_configdata/JWMarriottAerocity/GSTR-1-4A_01112021_30112021.CSV'
# df_gstr4a = pd.read_csv(file_name_gstr4a,names=['BILL_NO_1','GSTN','BILL_NO','INVOICE_DATE','AMOUNT','IGST','TOTAL_AMOUNT','CESS','CGST','SGST','VAT','PLACE']).dropna()
# pd_merge_gstr = pd.merge(pd_merge,df_gstr4a,on='BILL_NO')
# pd_merge_gstr.drop(['BILL_NO_1','INVOICE_DATE','AMOUNT','IGST','TOTAL_AMOUNT','CESS','CGST','SGST','VAT','PLACE','DISPLAY_NAME'],axis='columns', inplace=True)
# pd_merge_gstr.to_excel("outpt.xlsx",index=False) 

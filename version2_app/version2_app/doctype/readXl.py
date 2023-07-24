import pandas as pd
from pandas.core.indexes.base import Index
import numpy as np
# df_d140_read = pd.read_excel("/content/D140 _November 2021 (1).xlsx",engine='openpyxl')
# df = pd.DataFrame({
#     'ROOM': df_d140_read['ROOM'],
#     'GUEST_FULL_NAME':df_d140_read['GUEST_FULL_NAME'],
#     'TRX_DESC':df_d140_read['TRX_DESC'],
#     'BUSINESS_DATE':df_d140_read['BUSINESS_DATE'],
#     'CASHIER_DEBIT':df_d140_read['CASHIER_DEBIT'],
#     'CASHIER_CREDIT':df_d140_read['CASHIER_CREDIT'],
#     'CREDIT_CARD_SUPPLEMENT':df_d140_read['CREDIT_CARD_SUPPLEMENT'],
#     'TRX_NO':df_d140_read['TRX_NO']
# })
# # df.rename(columns={'TRX_NO': 'BILL_NO'}, inplace=True)
# # df["BILL_NO"]
# # df['ROOM'] = df['ROOM'].replace('AR',0)
# df["GUEST_FULL_NAME"] = df["GUEST_FULL_NAME"].replace(',MR|,MS|,Mr|,Ms|,ms|,mr|mr|ms|MR|MS|Ms|Mr','', regex=True)
# df.drop(df.index[df['ROOM'] == 'Passer'], inplace = True)
# df.drop(df.index[df['CASHIER_CREDIT'] != 0.0], inplace = True)
# print(df)
# file_name_d110 = "/home/caratred/Desktop/gst_configdata/JWMarriottAerocity/Reports/D110_Nov'21.xlsx"
df_d110_read = pd.read_excel("/home/caratred/Desktop/gst_configdata/JWMarriottAerocity/Reports/D110_Nov'21.xlsx",engine='openpyxl')
df_d110 = pd.DataFrame(df_d110_read, columns= ['BILL_NO','ROOM','DISPLAY_NAME','FOLIO_TYPE','BILL_GENERATION_DATE','TRX_DATE','TRANSACTION_DESCRIPTION','TRX_NO',]).dropna()
df_d110 = df_d110.astype({"ROOM": int})
# df_d110.rename(columns={'DISPLAY_NAME': 'GUEST_FULL_NAME'}, inplace=True)
# df_d110.rename(columns={'TRX_DATE': 'BUSINESS_DATE'}, inplace=True)
# # df_d110.rename(columns={'TRX_DATE': 'BUSINESS_DATE'}, inplace=True)
# pd_m = df.merge(df_d110,how="left",on=["TRX_NO"])
# # pd_m["BILL_NO"].fillna("missing", inplace = True)
# # pd_m["BILL_GENERATION_DATE"].fillna("missing", inplace = True)
# # pd_m["FOLIO_TYPE"].fillna("missing", inplace = True)
# pd_m.drop(['GUEST_FULL_NAME_y',"BUSINESS_DATE_x","ROOM_y","TRANSACTION_DESCRIPTION"],axis='columns', inplace=True)
# pd_m.rename(columns={'ROOM_x': 'ROOM'}, inplace=True)
# pd_m.rename(columns={'GUEST_FULL_NAME_x': 'GUEST_FULL_NAME'}, inplace=True)
# pd_m.rename(columns={'BUSINESS_DATE_y': 'BUSINESS_DATE'}, inplace=True)
# pd_m.to_excel("Results.xlsx",index=False)
# # print(pd_m,"_____________________________________________")
# # print(pd_room,"//////////////////")
# file_name_gstr4a = '/content/GSTR-1-4A_01112021_30112021 (2).CSV'
# df_gstr4a = pd.read_csv(file_name_gstr4a,names=['TITLE','GSTN','BILL_NO','INVOICE_DATE','AMOUNT','IGST','TOTAL_AMOUNT','CESS','CGST','SGST','VAT','PLACE'])
# # print(df_gstr4a,"////////////////")
# df_gstr4a = df_gstr4a.astype({"GSTN":str})
# pd_merge_gstr = pd.merge(pd_m,df_gstr4a,on="BILL_NO",how="left")
# pd_merge_gstr.drop(['TITLE','INVOICE_DATE','AMOUNT','IGST','TOTAL_AMOUNT','CESS','CGST','SGST','VAT','PLACE'],axis='columns', inplace=True)
# pd_merge_gstr['BUSINESS_DATE'] = pd.to_datetime(pd_merge_gstr['BUSINESS_DATE']).dt.strftime('%d-%b-%Y')
# pd_merge_gstr['BILL_GENERATION_DATE'] = pd.to_datetime(pd_merge_gstr['BILL_GENERATION_DATE']).dt.strftime('%d-%b-%Y')
# pd_total_result=pd_merge_gstr.drop_duplicates(subset=['TRX_NO'])
# pd_total_result.to_excel("gst_output.xlsx",index=False)
empty_report = pd.read_excel("/home/caratred/Desktop/gst_configdata/JWMarriottAerocity/gst_output (1).xlsx")
empty_dataframe = pd.DataFrame(empty_report)
# empty_dataframe.loc(empty_dataframe['TRX_DESC'] == "Package Rate")
df =empty_dataframe[empty_dataframe["TRX_DESC"].isin(["Package Rate"])]
# print(df,"????????????????????????????")
df['TRX_NO'] = df['TRX_NO'] - 1
# print(df,"//////////////////////////////////////")
pd_m = df.merge(df_d110,how="left",on=["TRX_NO"])
print(pd_m)
# pd_total = empty_report.merge(df_d110,how="left",on=["TRX_NO"])
# empty_dataframe.drop(empty_dataframe.index[empty_dataframe['FOLIO_TYPE'] != ' '], inplace = True)
# empty_dataframe.fillna(0,inplace=True)
# empty_dataframe.drop(empty_dataframe.index[empty_dataframe['FOLIO_TYPE']!= 0], inplace = True)
pd_m.to_excel("trans.xlsx",index=False)



# import frappe
# from frappe.model.document import Document
# import os
# import requests
# import json
# import string
# import frappe
# from frappe.utils import get_site_name
# import xlsxwriter
# import wget

# from os.path import expanduser
# home = expanduser("~")

# print(home,"/////////////")
# @frappe.whitelist(allow_guest=True)
# def Report_Download():
#     # try:
#     data = {"company":"MHKCP-01","items":[{"invoice_number":"MHKCP-70975","invoice_date":"2020-11-10","date":"2020-12-07","type_of_customer":"Un-registered","type":"B2C","name_of_client_/customer":"","customer_gstin/uin":"","invoice_value":1944.06,"taxable_value":1647.5,"rate":18,"gst_rate":18,"igst_rate":0,"igst_amount":0.0,"cgst_rate":9,"cgst_amount":148.28,"sgst/ut_rate":9,"sgst/_ut_gst_amount":148.28,"gst_compensation_cess_rate":0,"gst_compensation_cess_amount":0.0,"sum_of_taxes":296.56,"hsn":"996332","uqc":"IRD Dinner Food","quantity":"1"}]}
#     folder_path = frappe.utils.get_bench_path()
#     # company = frappe.get_doc('company',data['company'])
#     # path = folder_path + '/sites/' + company.site_name
#     workbook = xlsxwriter.Workbook(home+'/sample_report.xlsx')
#     worksheet = workbook.add_worksheet()
#     header = list(string.ascii_letters[26:52])
#     itemscount = data['items'][0]
#     merge_format = workbook.add_format({
#             'bold': 1,
#             'border': 1,
#             'align': 'center',
#             'valign': 'distributed'})
#     merge_format.set_text_wrap()
#     # set_text_wrap



    

#     if len(itemscount)>26:
#         header2 = []
#         for i in header:
#             header2.append('A'+i)
#         header.extend(header2)
#     keys = list(itemscount.keys())
#     worksheet.set_column(header[0]+":"+header[-1], 14)
#     worksheet.write_row('A1', keys,merge_format)
#     num = 2
#     for index,each in enumerate(data['items']):
#         if index!=1:
#             values = list(each.values())
#             worksheet.write_row('A'+str(num), values)
#             num+=1


#     workbook.close()
#     files_new = {"file": open(home+'/sample_report.xlsx', 'rb')}
#     payload_new = {
#         "is_private": 0,
#         "folder": "Home",
#         "doctype": "Invoices",
#         # "docname": data["invoice_number"],
#         # 'fieldname': 'b2c_qrinvoice'
#     }
#     upload_report = requests.post(
#         'http://0.0.0.0:8000/' + "api/method/upload_file",
#         files=files_new,
#         data=payload_new).json()
#     print(upload_report)    
#     # file_url
#     url = "http://0.0.0.0:8000"+upload_report['message']['file_url']

#     # wget.download(url)
#     return url
#     # except Exception as e:
#     #     return{"success":False,"message":str(e)}    
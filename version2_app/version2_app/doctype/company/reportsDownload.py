import frappe
from frappe.model.document import Document
import os
import requests
import json
import string
import frappe
from frappe.utils import get_site_name
import xlsxwriter
import wget



@frappe.whitelist(allow_guest=True)
def Report_Download(data):
    # try:
    folder_path = frappe.utils.get_bench_path()
    company = frappe.get_doc('company',data['company'])
    path = folder_path + '/sites/' + company.site_name
    workbook = xlsxwriter.Workbook('/home/caratred/hello.xlsx')
    worksheet = workbook.add_worksheet()
    header = list(string.ascii_letters[26:52])
    itemscount = data['items'][0]
    merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'distributed'})
    merge_format.set_text_wrap()



    

    if len(itemscount)>26:
        header2 = []
        for i in header:
            header2.append('A'+i)
        header.extend(header2)
    keys = list(itemscount.keys())
    worksheet.set_column(header[0]+":"+header[-1], 14)
    worksheet.write_row('A1', keys,merge_format)
    num = 2
    for index,each in enumerate(data['items']):
        if index!=1:
            values = list(each.values())
            worksheet.write_row('A'+str(num), values)
            num+=1


    workbook.close()
    # url = "http://0.0.0.0:8000/private/files/hello.xlsx"

    # wget.download(url)
    return{"success":True}
    # except Exception as e:
    #     return{"success":False,"message":str(e)}    
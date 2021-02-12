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
import pandas as pd
from urllib.parse import urljoin
from urllib.request import pathname2url
from os.path import expanduser
home = expanduser("~")

# host = "http://0.0.0.0:8000/"
@frappe.whitelist(allow_guest=True)
def Report_Download(data):
    
    try:
        if data['file_type']=="Excel":
            # print(data)
            company = frappe.get_doc('company',data['company'])
            host = company.host
            folder_path = frappe.utils.get_bench_path()
            fileName = data['report_name'].replace(" ","")
            workbook = xlsxwriter.Workbook(home+'/'+fileName+'.xlsx')
            worksheet = workbook.add_worksheet()
            header = list(string.ascii_letters[26:52])
            columnscount = data['columns']
            merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'align': 'center',
                    'valign': 'distributed'})
            merge_format.set_text_wrap()
            if len(columnscount)>26:
                header2 = []
                for i in header:
                    header2.append('A'+i)
                header.extend(header2)
            worksheet.set_column(header[0]+":"+header[-1], 14)
            worksheet.write_row('A1', columnscount,merge_format)
            num = 2
            for each in data['values']:
                worksheet.write_row('A'+str(num), each)
                num+=1
            workbook.close()
            files_new = {"file": open(home+'/'+fileName+'.xlsx', 'rb')}
            payload_new = {
                "is_private": 1,
                "folder": "Home"}
            upload_report = requests.post(
                host + "api/method/upload_file",
                files=files_new,
                data=payload_new).json()
            url = upload_report['message']['file_url']
            return url
        elif data['file_type'] == "CSV":
            fileName = data['report_name'].replace(" ","")
            df = pd.DataFrame(data['values'], columns = data['columns']) 
            print(df)
            df.to_csv(home+'/'+fileName+'.csv',index=False,columns=data['columns'])
            files_new = {"file": open(home+'/'+fileName+'.csv', 'rb')}
            payload_new = {
                "is_private": 1,
                "folder": "Home"
            }
            pathname = 'path/to/file/or/folder/'  
            # url = urllib.pathname2url(home+'/'+fileName+'.csv')  
            upload_report = requests.post(
                host + "api/method/upload_file",
                files=files_new,
                data=payload_new).json()
            url = upload_report['message']['file_url']
            return url#join('file:', pathname2url(home+'/'+fileName+'.csv'))



            # return{"success":True} 
    

    except Exception as e:
        print(str(e))
        return{"success":False,"message":str(e)}   


@frappe.whitelist(allow_guest=True)
def Report_Delete(data):
    try:
        folder_path = frappe.utils.get_bench_path()
        company = frappe.get_doc("company",data['company'])
        site = company.site_name
        filePath = folder_path+'/sites/'+site+data['filepath']
        os.remove(filePath)
        return{"success":True}
    except Exception as e:
        print(str(e),"  Report Delete")
        return{"success":False,"message":str(e)}    

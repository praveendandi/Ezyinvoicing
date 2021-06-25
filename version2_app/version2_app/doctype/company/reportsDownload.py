import frappe
from frappe.model.document import Document
import os,sys,traceback
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
from version2_app.version2_app.doctype.company.workbook_sheets import *
from os.path import expanduser
home = expanduser("~")

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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing Report_Download","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing Report_Delete","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return{"success":False,"message":str(e)}    


@frappe.whitelist(allow_guest=True)
def xlsx_workbook(data):
    # company = frappe.get_doc('company',data['company'])

    folder_path = frappe.utils.get_bench_path()
    # fileName = data['report_name'].replace(" ","")
    workbook = xlsxwriter.Workbook(home+'/'+'workbook.xlsx')
    # worksheet = workbook.add_worksheet()
    header = list(string.ascii_letters[26:52])
    # columnscount = data['columns']

    #B2B_Invoices
    b2bdata = B2B_Invoices(data)
    columnscount = b2bdata[0]
    
    if len(columnscount)>26:
        header2 = []
        for i in header:
            header2.append('A'+i)
        header.extend(header2)

    merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'distributed'})
    merge_format.set_text_wrap()
    worksheet1 = workbook.add_worksheet("B2B")
    worksheet1.set_column(header[0]+":"+header[-1])
    worksheet1.write_row('A1', columnscount,merge_format)
    num = 2
    for each in b2bdata[1]:
        worksheet1.write_row('A'+str(num), each)
        num+=1
    header = list(string.ascii_letters[26:52])
    b2cldata = B2CL_Invoices(data)
    columnscount = b2cldata[0]
    print(columnscount,"b2cl")
    if len(columnscount)>26:
        header2 = []
        for i in header:
            header2.append('A'+i)
        header.extend(header2)
    worksheet2 = workbook.add_worksheet("B2CL")
    worksheet2.set_column(header[0]+":"+header[-1])
    worksheet2.write_row('A1', columnscount,merge_format)
    num = 2
    for each in b2cldata[1]:
        worksheet2.write_row('A'+str(num), each)
        num+=1  

    # B2CS_Invoices
    header = list(string.ascii_letters[26:52])
    b2csdata = B2CS_Invoices(data)
    columnscount = b2csdata[0]
    
    if len(columnscount)>26:
        header2 = []
        for i in header:
            header2.append('A'+i)
        header.extend(header2)
    worksheet3 = workbook.add_worksheet("B2CS")
    worksheet3.set_column(header[0]+":"+header[-1])
    worksheet3.write_row('A1', columnscount,merge_format)
    num = 2
    for each in b2csdata[1]:
        worksheet3.write_row('A'+str(num), each)
        num+=1 


    #Excempted
    columnscount = ['Description','Nil Rated Supplies','Exempted(other than nil rated/non GST supply)','Non-GST Supplies']
    header = list(string.ascii_letters[26:52])
    if len(columnscount)>26:
        header2 = []
        for i in header:
            header2.append('A'+i)
        header.extend(header2)
    worksheet5 = workbook.add_worksheet("EXEMP")
    worksheet5.set_column(header[0]+":"+header[-1])
    worksheet5.write_row('A1', columnscount,merge_format)  

    #HSN_SAC_SUMMARY_REPORT
    header = list(string.ascii_letters[26:52])
    hsnsacdata = HSN_SAC_SUMMARY_REPORT(data)
    columnscount = hsnsacdata[0]
    
    if len(columnscount)>26:
        header2 = []
        for i in header:
            header2.append('A'+i)
        header.extend(header2)
    worksheet5 = workbook.add_worksheet("HSN SAC Summary")
    worksheet5.set_column(header[0]+":"+header[-1])
    worksheet5.write_row('A1', columnscount,merge_format)
    num = 2
    for each in hsnsacdata[1]:
        worksheet5.write_row('A'+str(num), each)
        num+=1 

    #DebitCreditNote
    header = list(string.ascii_letters[26:52])
    debitcreditnote = DebitCreditNote(data)
    columnscount = debitcreditnote[0]
    
    if len(columnscount)>26:
        header2 = []
        for i in header:
            header2.append('A'+i)
        header.extend(header2)
    worksheet6 = workbook.add_worksheet("CDNR")
    worksheet6.set_column(header[0]+":"+header[-1])
    worksheet6.write_row('A1', columnscount,merge_format)
    num = 2
    for each in debitcreditnote[1]:
        worksheet6.write_row('A'+str(num), each)
        num+=1
    
    
    #ATADJ
    columnscount=['Place Of Supply','Applicable % of Tax Rate','Rate','Gross Advance Received/Adjusted','Integrated Tax Amount','Central Tax Amount','State/UT Tax Amount','Cess Amount']
    header = list(string.ascii_letters[26:52])
    if len(columnscount)>26:
        header2 = []
        for i in header:
            header2.append('A'+i)
        header.extend(header2)
    worksheet7 = workbook.add_worksheet("ATADJ")
    worksheet7.set_column(header[0]+":"+header[-1])
    worksheet7.write_row('A1', columnscount,merge_format)      
    workbook.close()
    return True
        

import frappe
import operator
import pandas as pd

from frappe.utils import add_days, getdate, cstr
import os
import uuid

@frappe.whitelist()
def get_missing_count():
    '''
    get missing count
    '''
    # Todo add date condition 31-04-2023
    company = frappe.get_last_doc('company')
    print(company.einvoice_missing_date_feature)
    print(company.einvoice_missing_start_date)
    query = '''SELECT irn_number,invoice_date,invoice_category, COUNT(*) 
    AS data_count FROM `tabInvoices` WHERE invoice_date > DATE_SUB(NOW(), INTERVAL 8 DAY) AND irn_number is NULL 
    and invoice_type='B2B' and invoice_from != 'Web' GROUP BY invoice_date,invoice_category'''



    print(query)
    data = frappe.db.sql(query, as_dict=1)
    result = {}
    for cat in data:
        if str(cat['invoice_date']) in result.keys():
            result[str(cat['invoice_date'])][cat['invoice_category']
                                             ] = cat['data_count']

        else:
            result[str(cat['invoice_date'])] = {
                cat['invoice_category']: cat['data_count']
            }

    
    all_dates = []
    today = getdate()
    all_dates.append(str(today))
    counter = 7
    for day in range(counter):
        eight_days_ago = add_days(today, -(counter))
        all_dates.append(str(eight_days_ago))
        counter = counter-1
    
    for cal_date in all_dates:
        if cal_date not in result.keys():
            print(cal_date)
            result[cal_date] = {
                'Tax Invoice':0
            }


    print(result)
    final_result = []
    
    counter = 8
    for each_date in result.keys():
        each_dict = {
            "day": counter,
            'date': each_date
        }
        each_date = result[each_date]
        
        if 'Tax Invoice' in each_date.keys():
            each_dict['Tax Invoice'] = each_date['Tax Invoice']
        
        if 'Credit Invoice' in each_date.keys():
            each_dict['Credit Invoice'] = each_date['Credit Invoice']
        if 'Debit Invoice' in each_date.keys():
            each_dict['Debit Invoice'] = each_date['Debit Invoice']
        final_result.append(each_dict)
        counter = counter-1

   
    
    manual_query = '''SELECT irn_number,invoice_date, COUNT(*) 
    AS data_count FROM `tabInvoices` WHERE invoice_date > DATE_SUB(NOW(), 
    INTERVAL 8 DAY) AND irn_number is NULL and invoice_type='B2B' and invoice_from = 'Web' and invoice_category = 'Tax Invoice' GROUP BY invoice_date;'''
    manual_data = frappe.db.sql(manual_query, as_dict=1)
    # print(manual_data)
    for final in final_result:
        del final['day']
        for manual in manual_data:
            if final['date'] == str(manual['invoice_date']):
                final['manual'] = manual['data_count']
    
    manual_credit_query = '''SELECT irn_number,invoice_date, COUNT(*) 
    AS data_count FROM `tabInvoices` WHERE invoice_date > DATE_SUB(NOW(), 
    INTERVAL 8 DAY) AND irn_number is NULL and invoice_type='B2B' and invoice_category = 'Credit Invoice' GROUP BY invoice_date;'''
    manual_data = frappe.db.sql(manual_credit_query, as_dict=1)
    # print(manual_data)
    for final in final_result:
        # del final['day']
        for manual in manual_data:
            if final['date'] == str(manual['invoice_date']):
                if 'Credit Invoice' in final:
                    final['Credit Invoice'] = final['Credit Invoice']+manual['data_count']
                else:
                    final['Credit Invoice'] = manual['data_count']
    
    manual_credit_query = '''SELECT irn_number,invoice_date, COUNT(*) 
    AS data_count FROM `tabInvoices` WHERE invoice_date > DATE_SUB(NOW(), 
    INTERVAL 8 DAY) AND irn_number is NULL and invoice_type='B2B' and invoice_category = 'Debit Invoice' GROUP BY invoice_date;'''
    manual_data = frappe.db.sql(manual_credit_query, as_dict=1)
    print(manual_data)
    for final in final_result:
        # del final['day']
        for manual in manual_data:
            if final['date'] == str(manual['invoice_date']):
                if 'Debit Invoice' in final:
                    final['Debit Invoice'] = final['Debit Invoice']+manual['data_count']
                else:
                    final['Debit Invoice'] = manual['data_count']

    final_result.sort(key=operator.itemgetter('date'))

    return final_result

@frappe.whitelist()
def check_invoice_date_if_graterthan_days(invoice_number):
    company = frappe.get_last_doc('company')
    # print(company.einvoice_missing_date_feature)
    # print(company.einvoice_missing_start_date)
  
    doc = frappe.get_doc('Invoices', invoice_number)
    if doc:
        # invoice date cond
        if doc.invoice_date < company.einvoice_missing_start_date:
            return {"message":"valid Invoice date","success":True}
        else:
            today = getdate()
            eight_days_ago = add_days(today, -8)
            if doc.invoice_date <= eight_days_ago:
                return {"message":"Invoice date expired","success":False}
            else:
                return {"message":"valid Invoice date","success":True}
    else:
        return {"message":"Invoice not found","success":False}
    

@frappe.whitelist()
def download_due_and_expired_reports(report_type,month=None,year=None):
    company = frappe.get_last_doc('company')
    fields = ['invoice_number', 
	   'invoice_date',
	   'gst_number',
	   'trade_name','place_of_supply',
	   'invoice_category',
	   'total_invoice_amount','sez']
    print(month)
    print(year)
    query = '''SELECT '''
    for field in fields:
        query =  f'{query} {field},'
    if report_type == 'due_in':
        if company.einvoice_missing_date_feature == 1:
            query = '''{query} other_charges  FROM `tabInvoices` WHERE DATE(invoice_date) >= DATE('{company_date}') AND invoice_date > DATE_SUB(NOW(), INTERVAL 8 DAY) AND irn_number is NULL and invoice_type='B2B' ORDER BY invoice_date '''.format(query=query,company_date=company.einvoice_missing_start_date,month=month,year=year)
        else:
            query = '''{query} other_charges  FROM `tabInvoices` WHERE invoice_date > DATE_SUB(NOW(), INTERVAL 8 DAY) AND irn_number is NULL and invoice_type='B2B' ORDER BY invoice_date'''.format(query=query,month=month,year=year)
            print(query)
    else:
        if company.einvoice_missing_date_feature == 1:
            query = '''{query} other_charges  FROM `tabInvoices` WHERE DATE(invoice_date) >= DATE('{company_date}') AND invoice_date < DATE_SUB(NOW()-1, INTERVAL 7 DAY) AND irn_number is NULL and invoice_type='B2B' AND Month(invoice_date)={month} and Year(invoice_date)={year} ORDER BY invoice_date '''.format(query=query,company_date=company.einvoice_missing_start_date,month=month,year=year)
        else:
            query = '''{query} other_charges  FROM `tabInvoices` WHERE invoice_date < DATE_SUB(NOW()-1, INTERVAL 7 DAY) AND irn_number is NULL and invoice_type='B2B' AND Month(invoice_date)={month} and Year(invoice_date)={year} ORDER BY invoice_date '''.format(query=query,month=month,year=year)
            print(query)
    data = frappe.db.sql(query,as_list=1)
    fields.append('other_charges')
    print(data)
    if len(data) > 0 :
        df = pd.DataFrame(data)
        
        df.columns = fields
        cwd = os.getcwd()
        site_name = cstr(frappe.local.site)
        lowercase_str = uuid.uuid4().hex  

        file_path = f'{cwd}/{site_name}/public/files/{lowercase_str}.csv'
        response_path = f'files/{lowercase_str}.csv'

        df.to_csv(file_path)
        return {"success":True,'file_path':response_path}
    else:
        return {"success":False,'message':"No data found with selected filters"}



    
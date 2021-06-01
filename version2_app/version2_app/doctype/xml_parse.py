import json
import xmltodict
import frappe
import os
import re
import requests
import json
import traceback
import logging, frappe
from frappe.utils import cstr
import datetime
import importlib.util



@frappe.whitelist(allow_guest=True)
def extract_xml(file_list):
    try:
        cwd = os.getcwd() 
        site_name = cstr(frappe.local.site)
        date = datetime.datetime.today()
        date=str(date.strftime("%d"))+"-"+(date.strftime("%b")).upper()+"-"+date.strftime("%y")
        abs_path = os.path.dirname(os.getcwd())
        company_doc = frappe.get_last_doc("company")

        new_parsers = company_doc.new_parsers
        if new_parsers == 0:
            file_path = abs_path + '/apps/version2_app/version2_app/parsers/'+company_doc.name+'/invoice_parser.py'
        else:
            file_path = abs_path + '/apps/version2_app/version2_app/parsers_invoice/invoice_parsers/'+company_doc.name+'/invoice_parser.py'
        module_name = 'file_parsing'
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with open(cwd+"/"+site_name+file_list) as xml_file:
            data_dict = xmltodict.parse(xml_file.read())
        data=[]
        if isinstance(data_dict["FOLIO_DETAILS"]["LIST_G_BILL_NO"]["G_BILL_NO"], list):
            for each in data_dict["FOLIO_DETAILS"]["LIST_G_BILL_NO"]["G_BILL_NO"]:
                each['BILL_NO'] = each["BILL_NO"].strip()
                if company_doc.change_invoice_reconciliation_invoice_number == 1:
                    each['BILL_NO'] = module.invoiceNumberMethod(each['BILL_NO'])
                print(each['BILL_NO'])
                if "-" in each["BILL_GENERATION_DATE"]:
                    convert_bill_generation_date = datetime.datetime.strptime(each["BILL_GENERATION_DATE"], '%d-%b-%y').strftime('%Y-%m-%d')
                elif "." in each["BILL_GENERATION_DATE"]:
                    convert_bill_generation_date = datetime.datetime.strptime(each["BILL_GENERATION_DATE"], '%d.%b.%y').strftime('%Y-%m-%d')
                else:
                    convert_bill_generation_date = datetime.datetime.strptime(each["BILL_GENERATION_DATE"], '%d/%b/%y').strftime('%Y-%m-%d')
                if "-" in each["BILL_GENERATION_DATE_CHAR"]:
                    convert_bill_generation_date_char = datetime.datetime.strptime(each["BILL_GENERATION_DATE_CHAR"], '%d-%m-%y').strftime('%Y-%m-%d')
                elif "." in each["BILL_GENERATION_DATE_CHAR"]:
                    convert_bill_generation_date_char = datetime.datetime.strptime(each["BILL_GENERATION_DATE_CHAR"], '%d.%m.%y').strftime('%Y-%m-%d')
                else:
                    convert_bill_generation_date_char = datetime.datetime.strptime(each["BILL_GENERATION_DATE_CHAR"], '%d/%m/%y').strftime('%Y-%m-%d')
                if frappe.db.exists('Invoice Reconciliations', each["BILL_NO"]):
                    bill_doc = frappe.get_doc('Invoice Reconciliations', each["BILL_NO"])
                    if bill_doc.invoice_found=="No":
                        if frappe.db.exists('Invoices',each["BILL_NO"]):
                            bill_doc.invoice_found="Yes"
                            bill_doc.save()
                else:    
                    doc=frappe.get_doc({"doctype":"Invoice Reconciliations","bill_generation_date":convert_bill_generation_date,"folio_type":each["FOLIO_TYPE"],"bill_number":each["BILL_NO"],"bill_generation_date_char":convert_bill_generation_date_char,"fiscal_bill_number":each["FISCAL_BILL_NO"],"status":each["STATUS"],"display_name":each["DISPLAY_NAME"],"room":each["ROOM"]})   
                    doc.insert(ignore_permissions=True)
                    frappe.db.commit()
                if frappe.db.exists('Invoice Reconciliations', each["BILL_NO"]):
                    if frappe.db.exists('Invoices',each["BILL_NO"]):
                        invoice_doc = frappe.get_doc('Invoices',each["BILL_NO"])
                        invoice_doc.invoice_check = "Yes"
                        invoice_doc.save()
                        reconciliations_doc = frappe.get_doc('Invoice Reconciliations', each["BILL_NO"])
                        reconciliations_doc.invoice_found = "Yes"
                        reconciliations_doc.save()
                    else:
                        reconciliations_doc = frappe.get_doc('Invoice Reconciliations', each["BILL_NO"])
                        reconciliations_doc.invoice_found = "No"
                        reconciliations_doc.save()
        else:

            each = data_dict["FOLIO_DETAILS"]["LIST_G_BILL_NO"]["G_BILL_NO"]
            each['BILL_NO'] = each["BILL_NO"].strip()
            if company_doc.change_invoice_reconciliation_invoice_number == 1:
                each['BILL_NO'] = module.invoiceNumberMethod(each['BILL_NO'])
            print(each['BILL_NO'])
            if "-" in each["BILL_GENERATION_DATE"]:
                convert_bill_generation_date = datetime.datetime.strptime(each["BILL_GENERATION_DATE"], '%d-%b-%y').strftime('%Y-%m-%d')
            elif "." in each["BILL_GENERATION_DATE"]:
                convert_bill_generation_date = datetime.datetime.strptime(each["BILL_GENERATION_DATE"], '%d.%b.%y').strftime('%Y-%m-%d')
            else:
                convert_bill_generation_date = datetime.datetime.strptime(each["BILL_GENERATION_DATE"], '%d/%b/%y').strftime('%Y-%m-%d')
            if "-" in each["BILL_GENERATION_DATE_CHAR"]:
                convert_bill_generation_date_char = datetime.datetime.strptime(each["BILL_GENERATION_DATE_CHAR"], '%d-%m-%y').strftime('%Y-%m-%d')
            elif "." in each["BILL_GENERATION_DATE_CHAR"]:
                convert_bill_generation_date_char = datetime.datetime.strptime(each["BILL_GENERATION_DATE_CHAR"], '%d.%m.%y').strftime('%Y-%m-%d')
            else:
                convert_bill_generation_date_char = datetime.datetime.strptime(each["BILL_GENERATION_DATE_CHAR"], '%d/%m/%y').strftime('%Y-%m-%d')
            convert_bill_generation_date = datetime.datetime.strptime(each["BILL_GENERATION_DATE"], '%d-%b-%y').strftime('%Y-%m-%d')
            convert_bill_generation_date_char = datetime.datetime.strptime(each["BILL_GENERATION_DATE_CHAR"], '%d/%m/%y').strftime('%Y-%m-%d')
            if frappe.db.exists('Invoice Reconciliations', each["BILL_NO"]):
                bill_doc = frappe.get_doc('Invoice Reconciliations', each["BILL_NO"])
                if bill_doc.invoice_found=="No":
                    if frappe.db.exists('Invoices',each["BILL_NO"]):
                        bill_doc.invoice_found="Yes"
                        bill_doc.save()
            else:
                doc=frappe.get_doc({"doctype":"Invoice Reconciliations","bill_generation_date":convert_bill_generation_date,"folio_type":each["FOLIO_TYPE"],"bill_number":each["BILL_NO"],"bill_generation_date_char":convert_bill_generation_date_char,"fiscal_bill_number":each["FISCAL_BILL_NO"],"status":each["STATUS"],"display_name":each["DISPLAY_NAME"],"room":each["ROOM"]})   
                doc.insert(ignore_permissions=True)
                frappe.db.commit()
            if frappe.db.exists('Invoice Reconciliations', each["BILL_NO"]):
                if frappe.db.exists('Invoices',each["BILL_NO"]):
                    invoice_doc = frappe.get_doc('Invoices',each["BILL_NO"])
                    invoice_doc.invoice_check = "Yes"
                    invoice_doc.save()
                    reconciliations_doc = frappe.get_doc('Invoice Reconciliations', each["BILL_NO"])
                    reconciliations_doc.invoice_found = "Yes"
                    reconciliations_doc.save()
                else:
                    reconciliations_doc = frappe.get_doc('Invoice Reconciliations', each["BILL_NO"])
                    reconciliations_doc.invoice_found = "No"
                    reconciliations_doc.save()
        return True
    except Exception as e:
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}



@frappe.whitelist(allow_guest=True)
def invoice_check(data):
    filte=frappe.db.get_values('Invoice Reconciliations',filters={'bill_generation_date':['=', data["date"]]})
    invoice=frappe.db.get_values('Invoices',{"docstatus":0},"name")
    invoice=list(sum(invoice, ()))
    filte=list(sum(filte, ()))
    print(invoice)
    print(filte)
    data=[]
    for each in filte:
        if each in invoice:
            data.append({"Invoice Number":each, "Invoice Found":"Yes"})
        else:
            data.append({"Invoice Number":each, "Invoice Found":"No"})
    print(data)
    return data
            


    
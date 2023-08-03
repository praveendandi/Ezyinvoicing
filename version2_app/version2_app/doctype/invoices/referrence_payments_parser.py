import pdfplumber
from datetime import date
import datetime
import requests
import pandas as pd
import traceback,sys,os
import re
import json
import sys

from frappe.utils import get_site_name
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.items.items import updateitems
from version2_app.version2_app.doctype.invoice_payments.invoice_payments import insert_invoice_payments
folder_path = frappe.utils.get_bench_path()



def funForTilda(raw_data):
    items = [] 
    PaymentsData = []
    itemsort = 0
    for ind, i in enumerate(raw_data):
        company_doc = frappe.get_last_doc("company")
        dateformat = company_doc.invoice_item_date_format
        dt = ""
        if "-" in dateformat:
            dt = "-"
        elif "." in dateformat:
            dt = "."
        elif "/" in dateformat:
            dt = "/"
        pattern = re.compile("^([0-9]{2}\%s[0-9]{2}\%s[0-9]{2})+"%(dt,dt))
        check_date = re.findall(pattern, i)
        if len(check_date) > 0:
            item = dict()
            item_value = ""
            name = ""
            item_date = ""
            dt = i.strip()
            paymentTypes = GetPaymentTypes()
            paymentTypes  = [''.join(item) for item in paymentTypes['data']] 
            for index, j in enumerate(i.split(' ')):
                val = dt.split(" ")
                if index == 0 and len(val)>1:
                    item['date'] = j
                    item_date = item["date"]
                if len(val)>1:
                    item_value = val[-1]
                    item['item_value'] = float(item_value.replace(',', ''))
                if index == 1 and len(val)>1:
                    starting_index = i.index(j)
                    if "~" in i:
                        ending_index = i.find("~")
                        item["name"] = ((i[starting_index:ending_index]).strip()).replace("  "," ")
                        name = item["name"]
                    else:
                        ending_index = i.find(item_value)
                        item["name"] = ((i[starting_index:ending_index]).strip()).replace("  "," ")
                        name = item["name"]
                if len(val)>1:		
                    if 'SAC' in j:
                        item['sac_code'] = ''.join(filter(lambda j: j.isdigit(), j))
                    else:
                        item['sac_code'] = "No Sac"
                if len(val)>1:		
                    item['sort_order'] =  itemsort+1
                if "~" in i:
                    count = i.count(item_value)
                    end_index = i.find(item_value)
                    if count == 2:
                        end_index = i.index(item_value,end_index+1)
                    start_index = i.find("~")
                    item['referrence'] = i[start_index:end_index].replace("~","")
                if "~" not in i:
                    if item!={}:
                        item['referrence'] =" "
                item["card_number"] = ""
            if name in paymentTypes:
                next_to_item = raw_data[ind+1]
                if "Total" not in next_to_item and item_date not in next_to_item:
                    item["card_number"] = next_to_item.replace("XX/XX","")
                PaymentsData.append(item)
            itemsort+=1
            if item !={}:
                items.append(item)
    return PaymentsData            


def funForHash(raw_data):
    items = [] 
    itemsort = 0
    for i in raw_data:
        # print(i,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        i = i.strip()
        company_doc = frappe.get_last_doc("company")
        dateformat = company_doc.invoice_item_date_format
        dt = ""
        if "-" in dateformat:
            dt = "-"
        elif "." in dateformat:
            dt = "."
        elif "/" in dateformat:
            dt = "/"
        pattern = re.compile("^([0-9]{2}\%s[0-9]{2}\%s[0-9]{2})+"%(dt,dt))
        check_date = re.findall(pattern, i)
        if len(check_date) > 0 and "CGST" not in i and "SGST" not in i and "CESS" not in i and "VAT" not in i and "Cess" not in i and "Vat" not in i and "IGST" not in i and "Service Charge" not in i:
            item = dict()
            item_value = ""
            dt = i.strip()
            items_split = dt.split(" ")
            if len(items_split)>=3 and "." in items_split[-1]:
                item['date'] = items_split[0]
                item['item_value'] = float(items_split[-1].replace(",",""))
                item["name"] = (' '.join(items_split[1:-2])).strip()
                if "#" in item["name"]:
                    item["name"] = (item["name"].split("#")[0]).strip()
                if "Check" in item["name"]:
                    item["name"] = (item["name"].split("Check")[0]).strip()
                if "-FO" in item["name"]:
                    name_index = item["name"].index("-FO")
                    item["name"] = item["name"][:name_index]
                if "SIN" in item["name"]:
                    name_index = item["name"].index("SIN")
                    item["name"] = item["name"][:name_index]
                if "Ref" in item["name"]:
                    name_index = item["name"].index("Ref")
                    item["name"] = item["name"][:name_index]
                if "..." in item["name"]:
                    name_index = item["name"].index("...")
                    item["name"] = item["name"][:name_index]
                if "LOCAL" in item["name"]:
                    name_index = item["name"].index("LOCAL")
                    item["name"] = item["name"][:name_index]
                if "discount" in item["name"]:
                    name_index = item["name"].index("discount")
                    item["name"] = item["name"][:name_index]
                if "MOBILE" in item["name"]:
                    name_index = item["name"].index("MOBILE")
                    item["name"] = item["name"][:name_index]
                # if "-Rebate" in item["name"]:
                #     name_index = item["name"].rindex("-Rebate")
                #     item["name"] = item["name"][:name_index]
                if "Transfer Debit" in item["name"]:
                    if "(Amt" in i:
                        name_index = item["name"].rindex("(Amt")
                        item["name"] = item["name"][:name_index]
                if len(items_split[-2]) == 6 or len(items_split[-2]) == 8:
                    if items_split[-2].isdigit():
                        item['sac_code'] = items_split[-2]
                    else:
                        item["sac_code"] = "No Sac"
                else:
                    item["sac_code"] = "No Sac"
                item['sort_order'] =  itemsort+1
                if "#" in i:
                    start_index = i.find("#")
                    end_index = i.find(str(item["item_value"]))
                    # print(i," ",len(i)," ",item["item_value"])
                    sub = i[start_index:end_index].replace("#","")
                    item['referrence']=re.sub(" .*", "",sub)
                if "#" not in i:
                    if item!={}:
                        item['referrence'] =" "
            itemsort+=1
            # print(item,"====item")
            if item !={}:

                items.append(item)
    return items            



@frappe.whitelist()
def paymentsAndReferences(data):   
    try:
        start_time = datetime.datetime.utcnow()
        companyCheckResponse = frappe.get_doc("company",data['company'])
        site_folder_path = companyCheckResponse.site_name
        invoice = frappe.get_doc("Invoices",data['invoice_number'])
        file_path = folder_path+'/sites/'+site_folder_path+invoice.invoice_file
        content = []
        with pdfplumber.open(file_path) as pdf:
            count = len(pdf.pages)
            for index in range(count):
                first_page = pdf.pages[index]
                content.append(first_page.extract_text())

        raw_data = []
        for i in content:
            for j in i.splitlines():
                raw_data.append(j)

        # for tilda 
        if companyCheckResponse.referrence_separator_type == "Tilda":
            items = funForTilda(raw_data)
        if companyCheckResponse.referrence_separator_type == "Hash":
            items = funForHash(raw_data)

        
        paymentTypes = GetPaymentTypes()
        paymentTypes  = [''.join(each) for each in paymentTypes['data']]            
        
        PaymentsData = []
        total_items = []
       
        for each in items:
            if "CGST" in each["name"] or "SGST" in each["name"] or "CESS" in each["name"] or "VAT" in each["name"]:
                continue
            if each["name"] in paymentTypes:
                PaymentsData.append(each)
            else:
                total_items.append(each)
        # print(PaymentsData,"-=-=-apsspsj")        
        itemsData = {"invoice_number":data["invoice_number"],"items":total_items}
        updateitems(itemsData)
        paymentsinfo = {"invoice_number":data["invoice_number"],"items":PaymentsData}
        insert_invoice_payments(paymentsinfo)
        return total_items
    except Exception as e:
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}



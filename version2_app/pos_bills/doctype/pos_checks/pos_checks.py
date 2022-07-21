# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from operator import ge
from pickle import NONE
from typing_extensions import final
from webbrowser import get
import frappe
from frappe.model.document import Document
from frappe.utils import logger
import traceback, sys
import requests, json
# import datetime
from datetime import datetime
import os,re
import razorpay
from escpos.printer import Network
from frappe.integrations.utils import get_payment_gateway_controller
from version2_app.version2_app.doctype.paytm_integrate import *
from version2_app.passport_scanner.doctype.ml_utilities.common_utility import format_date
from datetime import date

class POSChecks(Document):
    pass


@frappe.whitelist(allow_guest=True)
def create_pos_bills(data):
    try:
        now = datetime.now()
        raw_data = data["payload"].split("\n")
        if len(raw_data) > 5:
            company_doc = frappe.get_doc("company",data["company"])
            data["mode"] = company_doc.mode
            data["doctype"] = "POS Checks"
            outlet_doc = frappe.get_doc("Outlets",data["outlet"])
            if outlet_doc.print == "Yes":
                outlet_printer = frappe.db.get_value("POS Print Settings",{"outlet":outlet_doc.name},"printer")
                printer_doc = frappe.get_doc("POS Printers",outlet_printer)
            extract_bills = extract_data(data["payload"],company_doc)
            if extract_bills["success"] == False:
                return extract_bills["message"]
            data.update(extract_bills["data"])
            folder_path = frappe.utils.get_bench_path()
            path = folder_path + '/sites/' + company_doc.site_name +"/public"
            logopath = path+outlet_doc.outlet_logo
            qrpath = path+outlet_doc.static_payment_qr_code
            added_text = ""
            invoice_number = ""
            added_text1 = ""
            if company_doc.enable_pos_extra_text == 1:
                text = add_extra_text_while_print(data["check_no"],data["outlet"],company_doc)
                if text["success"] == False:
                    return text
                added_text = (text["string"]).encode('utf-8')
                invoice_number = (text["invoice_number"]).encode('utf-8')
            if outlet_doc.print == "Yes" and data["check_type"] == "Normal Check":
                port = int(printer_doc.port) if printer_doc.port != "" else 9100
                if outlet_doc.payment_mode == "Dynamic":
                    if outlet_doc.payment_gateway == "Razorpay":
                        short_url = razorPay(data["total_amount"],data["check_no"],data["outlet"],company_doc)
                    if outlet_doc.payment_gateway == "Paytm":
                        short_url = paytmIntegrate(data["total_amount"],data["check_no"],data["outlet"],company_doc)
                    if short_url["success"]:
                        for count in range(0,outlet_doc.print_count):
                            if outlet_doc.print_count > 1:
                                if count == 0:
                                    added_text1 = "Guest Copy\n\n".encode("utf-8")
                                elif count == 1:
                                    added_text1 = "Merchant Copy\n".encode("utf-8")
                                elif count == 2:
                                    added_text1 = "Finance Copy\n".encode("utf-8")
                                if company_doc.enable_pos_extra_text == 1:
                                    added_text = added_text1+added_text.replace("Guest Copy\n".encode("utf-8"),"".encode("utf-8"))
                                    if count != 1:
                                        added_text = added_text1.replace("Merchant Copy\n".encode("utf-8"),"".encode("utf-8"))
                                else:
                                    added_text = added_text1.replace("Guest Copy\n".encode("utf-8"),"".encode("utf-8"))
                                    added_text = added_text1.replace("Merchant Copy\n".encode("utf-8"),"".encode("utf-8"))
                            give_print(data["payload"],printer_doc.printer_ip,logopath,qrpath,port,company_doc,added_text,invoice_number,short_url['short_url'])
                        data["printed"] = 1
                else:
                    for count in range(0,outlet_doc.print_count):
                        if outlet_doc.print_count > 1:
                            if count == 0:
                                added_text1 = "Guest Copy\n\n".encode("utf-8")
                            elif count == 1:
                                added_text1 = "Merchant Copy\n".encode("utf-8")
                            elif count == 2:
                                added_text1 = "Finance Copy\n".encode("utf-8")
                            if company_doc.enable_pos_extra_text == 1:
                                added_text = added_text1+added_text.replace("Guest Copy\n".encode("utf-8"),"".encode("utf-8"))
                                if count != 1:
                                    added_text = added_text1.replace("Merchant Copy\n".encode("utf-8"),"".encode("utf-8"))
                            else:
                                added_text = added_text1.replace("Guest Copy\n".encode("utf-8"),"".encode("utf-8"))
                                added_text = added_text1.replace("Merchant Copy\n".encode("utf-8"),"".encode("utf-8"))
                        give_print(data["payload"],printer_doc.printer_ip,logopath,qrpath,port,company_doc,added_text,invoice_number)
                    data["printed"] = 1
            if outlet_doc.print == "Yes" and data["check_type"] == "Check Closed":
                port = int(printer_doc.port) if printer_doc.port != "" else 9100
                pos_bills = send_pos_bills_gcb(company_doc,data)
                if pos_bills["success"] == False:
                    return pos_bills["message"]
                qrurl = company_doc.b2c_qr_url + pos_bills['data']
                for count in range(0,outlet_doc.print_count):
                    if outlet_doc.print_count > 1:
                        if count == 0:
                            added_text1 = "Guest Copy\n\n".encode("utf-8")
                        elif count == 1:
                            added_text1 = "Merchant Copy\n".encode("utf-8")
                        elif count == 2:
                            added_text1 = "Finance Copy\n".encode("utf-8")
                        if company_doc.enable_pos_extra_text == 1:
                            added_text = added_text1+added_text.replace("Guest Copy\n".encode("utf-8"),"".encode("utf-8"))
                            if count != 1:
                                added_text = added_text1.replace("Merchant Copy\n".encode("utf-8"),"".encode("utf-8"))
                        else:
                            added_text = added_text1.replace("Guest Copy\n".encode("utf-8"),"".encode("utf-8"))
                            added_text = added_text1.replace("Merchant Copy\n".encode("utf-8"),"".encode("utf-8"))
                    if count == 0:
                        if company_doc.pos_footer:
                            data["payload"] = data["payload"]+"\n"+company_doc.pos_footer+"\n"
                    extra_text_after_qr = None
                    if company_doc.pos_extra_text_after_qr:
                        extra_text_after_qr = company_doc.pos_extra_text_after_qr
                    give_print(data["payload"],printer_doc.printer_ip,logopath,qrpath,port,company_doc,added_text,invoice_number,qrurl,extra_text_after_qr)
                data["gcp_file_url"] = pos_bills['data']
                data["printed"] = 1
            doc = frappe.get_doc(data)
            doc.insert(ignore_permissions=True,ignore_links=True)
    except Exception as e:
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing create pos bills","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


def extract_data(payload,company_doc):
    try:
        data={}
        raw_data = payload.split("\n")
        total_amount = ""
        for line in raw_data:
            if company_doc.closed_check_reference in payload and company_doc.void_check_reference not in payload:
                data["check_type"] = "Check Closed"
                if company_doc.void_total_amt_regex: 
                    if re.match(company_doc.void_total_amt_regex,line.strip()):
                        total_amount_regex = re.findall(company_doc.bill_amount_regex,line.replace(" ",""))
                        total_amount = (total_amount_regex[0] if len(total_amount_regex) > 0 else "").replace(",","")
                        total_amount = total_amount.replace("-","")
                        total_amount = total_amount.lstrip(".")
                else:
                    total_amount = "0.00"
            elif company_doc.void_check_reference in payload:
                data["check_type"] = "Closed Void Check"
                if re.match(company_doc.void_total_amt_regex,line.strip()):
                    total_amount_regex = re.findall(company_doc.bill_amount_regex,line.replace(" ",""))
                    total_amount = (total_amount_regex[0] if len(total_amount_regex) > 0 else "").replace(",","")
                    total_amount = total_amount.replace("-","")
                    total_amount = total_amount.lstrip(".")
            else:
                data["check_type"] = "Normal Check"
                if re.match(company_doc.normal_check_total_amt_regex,line.strip()):
                    total_amount_regex = re.findall(company_doc.bill_amount_regex,line.replace(" ",""))
                    total_amount = (total_amount_regex[0] if len(total_amount_regex) > 0 else "").replace(",","")
                    total_amount = total_amount.replace("-","")
                    total_amount = total_amount.lstrip(".")
            if company_doc.name == "JP-2025":
                pattern = "[0-9]+/+[0-9]+\s+[0-9]+\s+GST+\s+[0-9]+|[0-9]+/+[0-9]+\s+[0-9]+\s+[GST]+[0-9]+|[0-9]+/+[0-9]+\s+[0-9]+|[0-9]+/+[0-9]+\s+[0-9]+\s+GST+[0-9]+"
                if re.match(pattern, line):
                    if "GST" not in line:
                        split_line = line.split(" ")
                        final_list = [i for i in split_line if i]
                        if len(final_list)>1:
                            data["check_no"] = final_list[1]
                            data["table_number"] = final_list[0]
                            data["no_of_guests"] = "0"
                    else:
                        split_line = line.split(" ")
                        final_list = [i for i in split_line if i]
                        if len(final_list)>=3:
                            data["check_no"] = final_list[1]
                            data["table_number"] = final_list[0]
                            data["no_of_guests"] = final_list[-1].replace("GST","")
            else:
                if company_doc.check_number_reference in line and "GSTIN" not in line and "GST IN" not in line:
                    check_regex = re.findall(company_doc.check_number_regex, line.strip())
                    check_string = check_regex[0] if len(check_regex)>0 else ""
                    check_no_regex = re.findall("\w+\d+",check_string)
                    data["check_no"] = check_no_regex[0] if len(check_no_regex) > 0 else ""
                if company_doc.table_number_reference in line and "GSTIN" not in line and "GST IN" not in line:
                    table_regex = re.findall(company_doc.table_number_regex, line.strip())
                    table_string = table_regex[0] if len(table_regex)>0 else ""
                    table_no_regex = table_string.split(" ")
                    data["table_number"] = table_no_regex[-1] if len(table_no_regex) > 1 else ""
                    if data["table_number"] == "" and len(table_no_regex) == 1:
                        data["table_number"] = table_no_regex[0] if "/" in table_no_regex[0] else ""
                if company_doc.guest_number_reference in line and "%" not in line and "GST No." not in line:
                    guestno_regex = re.findall(company_doc.guest_number_regex, line.strip())
                    print(guestno_regex)
                    guest_string = guestno_regex[0] if len(guestno_regex)>0 else ""
                    guest_no_regex = re.findall("\d+",guest_string)
                    data["no_of_guests"] = guest_no_regex[0] if len(guest_no_regex) > 0 else ""
                if company_doc.pos_date_reference:
                    if company_doc.pos_date_reference in line:
                        check_date = re.findall(company_doc.pos_date_regex,line)
                        checkdate = check_date[0] if len(check_date) > 0 else ""
                        if checkdate != "":
                            data["check_date"] = datetime.strptime(checkdate,company_doc.pos_check_date_format).strftime('%Y-%m-%d')
                        # data["check_date"] = format_date(
                        #     checkdate,
                        #     "yyyy-mm-dd",
                        # )
                        # today = date.today()
                        # print("Today date is: ", today)
                        # if today > data["check_date"]:
                        #     pass
        data["total_amount"] = str(total_amount)
        return {"success":True, "data":data}
    except Exception as e:
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing extract data","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

def give_print(text, ip, logo_path, qr_path,port,company_doc,added_text="",invoice_number="",short_url='',extra_text_after_qr=None):
    try:
        kitchen = Network(ip,int(port))  # Printer IP Address
        # kitchen = Network(ip)
        kitchen.set("CENTER", "A", "B")
        kitchen.image(img_source=logo_path)
        kitchen.hw('INIT')
        if company_doc.enable_pos_extra_text == 1:
            kitchen.set("CENTER", "A")
            kitchen.text('\n')
            kitchen._raw(added_text)
            kitchen.set("CENTER", "A","B")
            kitchen._raw(invoice_number)
            kitchen.set("CENTER", "A")
        else:
            kitchen.set("CENTER", "A","B")
            kitchen.text('\n')
        b = (text).encode('utf-8')
        split_amount = [each for each in text.split("\n") if re.match(company_doc.normal_check_total_amt_regex,each.strip())]
        if len(split_amount) == 1:
            split_string = text.split(split_amount[0])
            if len(split_string) == 2:
                kitchen.set("CENTER", "A")
                kitchen._raw(split_string[0].encode('utf-8'))
                kitchen.set("CENTER", "A","B",1,2)
                kitchen._raw(split_amount[0].encode('utf-8'))
                kitchen.set("CENTER", "A")
                kitchen._raw(split_string[1].encode('utf-8'))
            else:
                kitchen._raw(b)
        else:
            kitchen._raw(b)
        kitchen.hw('INIT')
        kitchen.set("CENTER", "A", "B")
        if short_url!='':
            kitchen.qr(short_url,size=7)
            kitchen.hw('INIT')
        else:
            kitchen.image(qr_path)
            kitchen.hw('INIT')
        if extra_text_after_qr:
            kitchen.set("CENTER", "A")
            kitchen.text('\n')
            kitchen._raw(extra_text_after_qr.encode('utf-8'))    
        kitchen.cut()
        kitchen.hw('INIT')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing give print","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

def razorPay(total_bill_amount,check_no,outlet,company_doc):
    try:
        razorpay_doc = frappe.get_doc("Razorpay Settings")
        sec = razorpay_doc.get_password(fieldname='api_secret',raise_exception=True)
        client = razorpay.Client(auth=(razorpay_doc.api_key, sec))
        # order_currency = 'INR'
        # order_receipt = check_no+" "+outlet
        data = {
            "customer": {
            "name": outlet+" "+"POS Bill",
            "email": "",
            "contact": ""},
            "type": "link",
            "amount": int(total_bill_amount.replace(".","")),
            "currency": "INR",
            "description": outlet+"\n"+check_no
            }
        notes = {'Shipping address': company_doc.address_1+", "+company_doc.location+", "+str(company_doc.pincode)}
        # test = client.order.create(amount=float(order_amount), currency=order_currency, receipt=order_receipt, notes=notes)
        test = client.invoice.create(data=data)
        return {"success":True, "short_url":test["short_url"]}
    except Exception as e:
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing razorPay","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

def add_extra_text_while_print(check_no,outlet,company_doc):
    try:
        if company_doc.pos_text:
            text = company_doc.pos_text
        else:
            text = ""
        outlet_doc = frappe.get_doc("Outlets",outlet)
        if outlet_doc.invoice_number_format:
            format = outlet_doc.invoice_number_format
            monformat = ""
            yearformat = ""
            dayformat = ""
            x = datetime.now()
            if format:
                countofy = format.count("Y")
                if countofy!=0:
                    yearformat = x.strftime("%y") if countofy == 2 else x.strftime("%Y")
                countofm = format.count("M")
                if countofm!=0:
                    monformat = x.strftime("%m") if countofy == 2 else x.strftime("%m")
                countofd = format.count("D")
                if countofd!=0:
                    dayformat = x.strftime("%d")
        
            # company_name = '{}'.format(company_doc.company_name)+"\n"+company_doc.address_1+"\n"
            # address = company_doc.address_2+", "+company_doc.location+"-"+str(company_doc.pincode)+", INDIA"
            # mobile = "\nTel:"+company_doc.phone_number+" "+outlet_doc.website
            # gst_details = "\nGSTIN--:{}, FSSAI {}\nTIN NO:{} CIN NO:{}\nPlace Of Supply:{}\nRETAIL INVOICE\n".format(outlet_doc.gstin,outlet_doc.fssai,outlet_doc.tin_no,outlet_doc.cin_no,company_doc.place_of_supply)
            invoice_number = "\nInvoice No "+yearformat+monformat+dayformat+check_no + "\n"
        else:
            invoice_number = ""
        return {"success":True,"string":text,"invoice_number":invoice_number}
    except Exception as e:
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing add_extra_text_while_print","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)
def print_pos_bill(data):
    try:
        check_doc = frappe.get_doc("POS Checks",data["name"])
        company_doc = frappe.get_doc("company",check_doc.company)
        outlet_doc = frappe.get_doc("Outlets",check_doc.outlet)
        if company_doc.enable_pos_extra_text == 1:
            text = add_extra_text_while_print(check_doc.check_no,check_doc.outlet,company_doc)
            if text["success"] == False:
                return text
            added_text = (text["string"]).encode('utf-8')
            x = check_doc.creation
            format = outlet_doc.invoice_number_format
            monformat = ""
            yearformat = ""
            dayformat = ""
            if format:
                countofy = format.count("Y")
                if countofy!=0:
                    yearformat = x.strftime("%y") if countofy == 2 else x.strftime("%Y")
                countofm = format.count("M")
                if countofm!=0:
                    monformat = x.strftime("%m") if countofy == 2 else x.strftime("%m")
                countofd = format.count("D")
                if countofd!=0:
                    dayformat = x.strftime("%d")
            invoice_number = ("\nInvoice No "+yearformat+monformat+dayformat+check_doc.check_no + "\n").encode('utf-8')
        outlet_values = frappe.db.get_values("Outlets",{"outlet_name":check_doc.outlet},["static_payment_qr_code","outlet_logo","payment_mode","name","payment_gateway"],as_dict=1)
        printer_settings = frappe.db.get_value("POS Print Settings",{"outlet":outlet_values[0]["name"]},["printer"])
        printer_doc = frappe.get_doc("POS Printers",printer_settings)
        folder_path = frappe.utils.get_bench_path()
        path = folder_path + '/sites/' + company_doc.site_name +"/public"
        new_path = folder_path + '/sites/' + company_doc.site_name
        if "private" not in outlet_values[0]["outlet_logo"]:
            logopath = path+outlet_values[0]["outlet_logo"]
        else:
            logopath = new_path+outlet_values[0]["outlet_logo"]
        if "private" not in outlet_values[0]["static_payment_qr_code"]:
            qr_path = path+outlet_values[0]["static_payment_qr_code"]
        else:
            qr_path = new_path+outlet_values[0]["static_payment_qr_code"]
        # b = (company_name+address+mobile+gst_details+check_doc.payload+"\n").encode('utf-8')
        kitchen = Network(printer_doc.printer_ip,int(printer_doc.port) if printer_doc.port != "" else 9100)  # Printer IP Address
        # kitchen = Network(printer_doc.printer_ip)
        kitchen.set("CENTER", "A", "B")
        kitchen.image(img_source=logopath)
        kitchen.hw('INIT')
        if company_doc.enable_pos_extra_text == 1:
            kitchen.set("CENTER", "A")
            kitchen.text('\n')
            kitchen._raw(added_text)
            kitchen.set("CENTER", "A","B")
            kitchen._raw(invoice_number)
            kitchen.set("CENTER", "A")
        else:
            kitchen.set("CENTER", "A","B")
            kitchen.text('\n')
        payload_text = check_doc.payload
        split_amount = [each for each in payload_text.split("\n") if re.match(company_doc.normal_check_total_amt_regex,each.strip())]
        if len(split_amount) == 1:
            split_string = payload_text.split(split_amount[0])
            if len(split_string) == 2:
                kitchen.set("CENTER", "A")
                kitchen._raw(split_string[0].encode('utf-8'))
                kitchen.set("CENTER", "A","B",1,2)
                kitchen._raw(split_amount[0].encode('utf-8'))
                kitchen.set("CENTER", "A")
                kitchen._raw(split_string[1].encode('utf-8'))
            else:
                b = (payload_text).encode('utf-8')
                kitchen._raw(b)
        else:
            b = (payload_text).encode('utf-8')
            kitchen._raw(b)
        kitchen.hw('INIT')
        kitchen.set("CENTER", "A", "B")
        if check_doc.check_type == "Normal Check":
            if outlet_values[0]["payment_mode"]=="Dynamic":
                if outlet_values[0]["payment_gateway"] == "Razorpay":
                    razor_pay = razorPay(check_doc.total_amount,check_doc.check_no,check_doc.outlet,company_doc)
                if outlet_values[0]["payment_gateway"] == "Paytm":
                    razor_pay = paytmIntegrate(check_doc.total_amount,check_doc.check_no,check_doc.outlet,company_doc)               
                    if razor_pay["success"] == False:
                        return razor_pay["message"]
                    kitchen.qr(razor_pay['short_url'],size=7)
                    kitchen.hw('INIT')         
            else:
                kitchen.image(qr_path)
                kitchen.hw('INIT')
        elif check_doc.check_type == "Check Closed":
            qrurl = company_doc.b2c_qr_url + check_doc.gcp_file_url
            kitchen.qr(qrurl,size=7)
            kitchen.hw('INIT')
        else:
            pass
        kitchen.cut()
        kitchen.hw('INIT')
        return {"success":True,"message":"Printed Successfully"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing give print","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}
    

def send_pos_bills_gcb(company,b2c_data):
    try:
        # b2c_data = json.dumps(data)
        if company.pms_property_url:
            b2c_data["file_url"]= company.pms_property_url
        b2c_data["invoice_number"] = b2c_data["check_no"]
        b2c_data["pos"] = True
        if company.proxy == 1:
            proxyhost = company.proxy_url
            proxyhost = proxyhost.replace("http://","@")
            proxies = {'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost}
        headers = {'Content-Type': 'application/json'}
        if company.proxy == 0:
            if company.skip_ssl_verify == 0:
                json_response = requests.post(
                    "https://gst.caratred.in/ezy/api/addJsonToGcb",
                    headers=headers,
                    json=b2c_data,verify=False)
            else:
                json_response = requests.post(
                    "https://gst.caratred.in/ezy/api/addJsonToGcb",
                    headers=headers,
                    json=b2c_data,verify=False)
            response = json_response.json()
            if response["success"] == False:
                return {
                    "success": False,
                    "message": response["message"]
                }
        else:
            json_response = requests.post(
                "https://gst.caratred.in/ezy/api/addJsonToGcb",
                headers=headers,
                json=b2c_data,
                proxies=proxies,verify=False)
            response = json_response.json()
            if response["success"] == False:
                return {
                    "success": False,
                    "message": response["message"]
                }
        return {"success":True, "data": response['data']}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing send pos bills gcb","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


def get_outlet_from_check(payload):
    try:
        get_outlets = frappe.db.get_list("Outlets",fields=["name", "outlet_short_name"])
        if len(get_outlets) > 0:
            data = {}
            for each in get_outlets:
                if each["name"] in payload:
                    data = each
                    break
            if bool(data):
                return {"success": True, "outlet": data["name"], "outlet_short_name": data["outlet_short_name"]}
            return {"success": False}
        else:
            return {"success": False, "outlet": "No outlet found"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing get_outlet_from_check","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


@frappe.whitelist(allow_guest=True)
def update_check_in_items(invoice_number=None, check_name=None):
    try:
        if invoice_number and check_name:
            frappe.db.set_value("POS Checks", check_name, {"attached_to": invoice_number, "sync": "Yes"})
            get_check_details = frappe.db.get_value("POS Checks",check_name, "pos_check_reference_number")
            if get_check_details:
                if not frappe.db.exists("Invoices", {"invoice_from": "File"}):
                    if not frappe.db.exists("Items",{"parent":invoice_number, "reference_check_number": get_check_details}):
                        return {"success": False, "message": "Check not found in this invoice"}
                    get_check_details = frappe.db.get_value("Items",{"parent":invoice_number, "reference_check_number": get_check_details}, "name")
                    if get_check_details:
                        frappe.db.set_value("Items",get_check_details,{"pos_check":check_name})
            frappe.db.commit()
            return {"success": True, "message": "POS Check Updated"}
        return {"success": False, "message": "invoice number and check_name is mandatory"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing update_check_in_items","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}
    

def update_pos_check(doc, method=None):
    try:
        if doc.check_no and doc.check_date:
            ref = doc.check_date+"-"+doc.check_no
            get_doc = frappe.get_doc("POS Checks", doc.name)
            get_doc.pos_check_reference_number = ref
            get_doc.save()
            if frappe.db.exists("Items", {"reference_check_number":ref}):
                invoice_number = frappe.db.get_value("Items", {"reference_check_number":ref}, ["parent"])
                frappe.db.sql("""update `tabItems` set pos_check='{}' where reference_check_number='{}'""".format(doc.name, ref))
                frappe.db.sql("""update `tabPOS Checks` set attached_to='{}', sync='Yes' where name='{}'""".format(invoice_number, doc.name))
                frappe.db.commit()
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing update_pos_check","line No:{}\n{}".format(exc_tb.tb_lineno,str(e)))
        return {"success":False,"message":str(e)}
    
@frappe.whitelist(allow_guest=True)   
def get_pos_checks_clbs(summary=None):
    try:
        if summary:
            get_invoices = frappe.db.get_list("Invoices",filters={"summary":summary},pluck="name")
            if len(get_invoices) > 0:
                get_pos_checks = frappe.db.get_list("POS Checks",filters=[["attached_to","in",get_invoices]],fields=["pos_bill as document","check_no as name"])
                if len(get_pos_checks) > 0:
                    return {"success": True, "checks": get_pos_checks}
                return {"success": False, "message": "No checks found"}
            return {"success": False, "message": "No invoices found"}
        return {"success": False, "message": "summary name is mandatory"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing get_pos_checks_clbs","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}
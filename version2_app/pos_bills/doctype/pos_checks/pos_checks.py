# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import logger
import traceback, sys
import requests, json
import os,re
import razorpay
from escpos.printer import Network
from frappe.integrations.utils import get_payment_gateway_controller
frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("api", allow_site=True, file_count=50)

class POSChecks(Document):
	pass


@frappe.whitelist(allow_guest=True)
def create_pos_bills(data):
	try:
		raw_data = data["payload"].split("\n")
		if len(raw_data) > 5:
			company_doc = frappe.get_doc("company",data["company"])
			data["mode"] = company_doc.mode
			data["doctype"] = "POS Checks"
			outlet_doc = frappe.get_doc("Outlets",data["outlet"])
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
			port = int(printer_doc.port) if printer_doc.printer_ip != "" else 9100
			if outlet_doc.print == "Yes" and data["check_type"] == "Normal Check":
				if outlet_doc.payment_mode == "Dynamic":
					short_url = razorPay(data["total_amount"],data["check_no"],data["outlet"],company_doc)
					if short_url["success"]:
						give_print(data["payload"],printer_doc.printer_ip,logopath,qrpath,port,short_url['short_url'])
						data["printed"] = 1
				else:
					give_print(data["payload"],printer_doc.printer_ip,logopath,port,qrpath)
					data["printed"] = 1
			if outlet_doc.print == "Yes" and data["check_type"] == "Check Closed":
				pos_bills = send_pos_bills_gcb(company_doc,data)
				if pos_bills["success"] == False:
					return pos_bills["message"]
				qrurl = company_doc.b2c_qr_url + pos_bills['data']
				give_print(data["payload"],printer_doc.printer_ip,logopath,qrpath,port,qrurl)
				data["gcp_file_url"] = pos_bills['data']
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
						total_amount_regex = re.findall("\d+\.\d+",line.replace(" ",""))
						total_amount = (total_amount_regex[0] if len(total_amount_regex) > 0 else "").replace(",","")
				else:
					total_amount = "0.00"
			elif company_doc.void_check_reference in payload:
				data["check_type"] = "Closed Void Check"
				if re.match(company_doc.void_total_amt_regex,line.strip()):
					total_amount_regex = re.findall("\d+\.\d+",line.replace(" ",""))
					total_amount = (total_amount_regex[0] if len(total_amount_regex) > 0 else "").replace(",","")
			else:
				data["check_type"] = "Normal Check"
				if re.match(company_doc.normal_check_total_amt_regex,line.strip()):
					total_amount_regex = re.findall("\d+\.\d+",line.replace(" ",""))
					total_amount = (total_amount_regex[0] if len(total_amount_regex) > 0 else "").replace(",","")
			if company_doc.check_number_reference in line:
				check_regex = re.findall(company_doc.check_number_regex, line.strip())
				check_string = check_regex[0] if len(check_regex)>0 else ""
				check_no_regex = re.findall("\d.+",check_string)
				data["check_no"] = check_no_regex[0] if len(check_no_regex) > 0 else ""
			if company_doc.table_number_reference in line:
				table_regex = re.findall(company_doc.table_number_regex, line.strip())
				table_string = table_regex[0] if len(table_regex)>0 else ""
				table_no_regex = table_string.split(" ")
				data["table_number"] = table_no_regex[-1] if len(table_no_regex) > 1 else ""
			if company_doc.guest_number_reference in line and "%" not in line and "GST No." not in line:
				guestno_regex = re.findall(company_doc.guest_number_regex, line.strip())
				print(guestno_regex)
				guest_string = guestno_regex[0] if len(guestno_regex)>0 else ""
				guest_no_regex = re.findall("\d+",guest_string)
				data["no_of_guests"] = guest_no_regex[0] if len(guest_no_regex) > 0 else ""
		data["total_amount"] = str(total_amount)
		return {"success":True, "data":data}
	except Exception as e:
		print(str(e))
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("Ezy-invoicing extract data","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
		return {"success":False,"message":str(e)}

def give_print(text, ip, logo_path, qr_path,port,short_url=''):
	try:
		b = text.encode('utf-8')
		kitchen = Network(ip,port)  # Printer IP Address
		kitchen.set("CENTER", "A", "B")
		kitchen.image(img_source=logo_path)
		kitchen.hw('INIT')
		kitchen.set("CENTER", "A", "B")
		kitchen.text('\n')
		kitchen._raw(b)
		kitchen.hw('INIT')
		kitchen.set("CENTER", "A", "B")
		if short_url!='':
			kitchen.qr(short_url,size=7)
			kitchen.hw('INIT')
		else:
			kitchen.image(qr_path)
			kitchen.hw('INIT')
		kitchen.cut()
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

@frappe.whitelist(allow_guest=True)
def print_pos_bill(data):
	try:
		check_doc = frappe.get_doc("POS Checks",data["name"])
		company_doc = frappe.get_doc("company",check_doc.company)
		outlet_values = frappe.db.get_values("Outlets",{"outlet_name":check_doc.outlet},["static_payment_qr_code","outlet_logo","payment_mode","name"],as_dict=1)
		printer_settings = frappe.db.get_value("POS Print Settings",{"outlet":outlet_values[0]["name"]},["printer"])
		printer_doc = frappe.get_doc("POS Printers",printer_settings)
		folder_path = frappe.utils.get_bench_path()
		path = folder_path + '/sites/' + company_doc.site_name +"/public"
		logopath = path+outlet_values[0]["outlet_logo"]
		qr_path = path+outlet_values[0]["static_payment_qr_code"]
		b = (check_doc.payload).encode('utf-8')
		kitchen = Network(printer_doc.printer_ip,int(printer_doc.port) if printer_doc.port != "" else 9100)  # Printer IP Address
		kitchen.set("CENTER", "A", "B")
		kitchen.image(img_source=logopath)
		kitchen.hw('INIT')
		kitchen.set("CENTER", "A", "B")
		kitchen.text('\n')
		kitchen._raw(b)
		kitchen.hw('INIT')
		kitchen.set("CENTER", "A", "B")
		if check_doc.check_type == "Normal Check":
			if outlet_values[0]["payment_mode"]=="Dynamic":
				razor_pay = razorPay(check_doc.total_amount,check_doc.check_no,check_doc.outlet,company_doc)
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
		return {"success":True,"message":"Printed Successfully"}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("Ezy-invoicing give print","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
		return {"success":False,"message":str(e)}
	

def send_pos_bills_gcb(company,b2c_data):
	try:
		# b2c_data = json.dumps(data)
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
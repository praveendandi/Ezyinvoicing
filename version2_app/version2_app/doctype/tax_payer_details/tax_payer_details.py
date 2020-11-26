# -*- coding: utf-8 -*-
# Copyright (c) 2020, Caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

host = "http://localhost:8000/api/method/"

class TaxPayerDetails(Document):
	pass
import requests,random
import frappe
Headers = {
    'Content-Type': 'application/json'
} 
import datetime

@frappe.whitelist(allow_guest=True)
def getTaxPayerDetails(data):

	if data['type'] == "All":
		if data['status'] == "All":
			taxpayerdata = frappe.db.get_list('TaxPayerDetail',
				# filters={
				# 	'Status': data['status']
				# },
				fields=['gst_number','legal_name','trade_name','creation','status'],
				order_by=data['sortKey'],
				start=data['start'],
				page_length=data['end'],
				as_list=True
			)
		else:
			taxpayerdata = frappe.db.get_list('TaxPayerDetail',
				filters={
					'Status': data['status']
				},
				fields=['gst_number','legal_name','trade_name','creation','status'],
				order_by=data['sortKey'],
				start=data['start'],
				page_length=data['end'],
				as_list=True
			)

	else:
		taxpayerdata = frappe.db.get_list('TaxPayerDetail',
		filters={
			data['key']: ['like', '%'+data['value']+'%']
		},
		fields=['gst_number','legal_name','trade_name','creation','status'],
		order_by=data['sortKey'],
		start=data['start'],
		page_length=data['end'],
		as_list=True)
	data = []
	indata = []
	countquery = frappe.db.get_list('TaxPayerDetail',
			fields=['count(name) as count']
		)
	count={"gstCount":countquery[0]['count']}
	for each in list(taxpayerdata):
		listData = {}
		listData['gstNumber'] = each[0]
		listData['trade_name'] = each[2]
		listData['legal_name'] = each[1]
		listData['creation'] = each[3]
		listData['status'] = each[4]
		invoiceData = frappe.db.get_list('Invoices',filters={'gst_number':each[0]},fields=['has_credit_items','name','invoice_number'],as_list=True)
		# listData['']
		listData['invoice_count'] = len(list(invoiceData))
		# credit_count = [x for x in list(invoiceData) if "Yes" in list(x)]
		creditCount = 0
		for each in list(invoiceData):
			if "Yes" in list(each):
				creditCount+=1
		listData['credit_count'] = creditCount
		data.append(listData)
		
	return {"success":True,"data":data,"count":count}

def request_get(api, data):
	try:
		print(api,data)
		headerData = {
			"user_name": data['apidata']["username"],
			"password": data['apidata']["password"],
			"gstin": data['apidata']['gst'],
			"requestid": str(random.randrange(1, 10**4)),
			"Authorization": "Bearer " + data["apidata"]["token"]
		}
		# print(headerData)
		raw_response = requests.get(api, headers=headerData)
		print(raw_response,"----------------")
		if raw_response.status_code == 200:
			return raw_response.json()
		else:
			print(raw_response)
	except Exception as e:
		print(e,"request get")

@frappe.whitelist(allow_guest=True)
def TaxPayerDetails(data):
	'''
	get TaxPayerDetail from gsp   gstNumber, code, apidata
	'''
	try:
		fields = ['gst_number','name','legal_name','address_1','address_2','location','pincode','gst_status','tax_type','trade_name','phone_number','state_code','status','block_status','company']
		tay_payer_details = frappe.db.get_value('TaxPayerDetail', data['gstNumber'],fields,as_dict=1)
		if tay_payer_details is None:
		
			companyCheckResponse = requests.post(host+"version2_app.version2_app.doctype.invoices.invoices.check_company_exist",headers=Headers,json={"code":data['code']}).json()
			companyApis = companyCheckResponse['message']['data']
			if companyCheckResponse['message']['success'] == True:
				gspApiDataResponse = requests.post(host+companyApis['gsp_api_data'],headers=Headers,json={"data":{"code":companyCheckResponse['message']['data']['name'],"mode":companyCheckResponse['message']['data']['mode'],"provider":companyCheckResponse['message']['data']['provider']}}).json()
				if gspApiDataResponse['message']['success'] == True:
					# print(gspApiDataResponse)
					GspData = {"gstNumber":data['gstNumber'],"code":data['code'],"apidata":gspApiDataResponse['message']['data']}
					response = request_get(gspApiDataResponse['message']['data']['get_taxpayer_details']+ data['gstNumber'],
										GspData)
					if response['success']:
							
						details = response['result']
						if (details['AddrBnm'] == "") or (details['AddrBnm'] == None):
							if (details['AddrBno'] != "") or (details['AddrBno'] != ""):
								details['AddrBnm'] = details['AddrBno']
						if (details['AddrBno'] == "") or (details['AddrBno'] == None):
							if (details['AddrBnm'] != "") or (details['AddrBnm'] != None):
								details['AddrBno'] = details['AddrBnm']
						if (details['TradeName'] == "") or (details['TradeName'] == None):
							if (details['LegalName'] != "") or (details['TradeName'] !=None):
								details['TradeName'] = details['LegalName']
						if (details['LegalName'] == "") or (details['LegalName'] == None):
							if (details['TradeName'] != "") or (details['TradeName'] != None):
								details['LegalName'] = details['TradeName']
						if (details['AddrLoc'] == "") or (details['AddrLoc'] == None):
							details['AddrLoc'] = "New Delhi"		
						
						if len(details["AddrBnm"]) < 3:
							details["AddrBnm"] = details["AddrBnm"]+"    "
						if len(details["AddrBno"]) < 3:
							details["AddrBno"] = details["AddrBno"] + "    " 		
						tax_payer = {
							'doctype':
							'TaxPayerDetail',
							"gst_number":
							details['Gstin'],
							"email": " ",
							"phone_number": " ",
							"legal_name":
							details['LegalName'],
							"address_1":
							details['AddrBnm'],
							"address_2":
							details['AddrBno'],
							"location":
							details['AddrLoc'],
							"pincode":
							details['AddrPncd'],
							"gst_status":
							details['Status'],
							"tax_type":
							details['TxpType'],
							"company":
							data['code'],
							"trade_name":
							details['TradeName'],
							"state_code":
							details['StateCode'],
							"last_fetched":
							datetime.date.today(),
							"address_floor_number":
							details['AddrFlno'],
							"address_street":
							details['AddrSt'],
							"block_status":
							''
							if details['BlkStatus'] == None else details['BlkStatus'],
							"status":details['Status']
							}
						if details['Status'] == "ACT":
							tax_payer['status'] = "Active"
						else:
							tax_payer['status'] = "In-Active"


						
						return {"success":True,"data":tax_payer,"update":False}
						
					else:
						return {"success":False,"message":response['message'],"response":response}

				else:
					return {"success":False,"message":gspApiDataResponse['message']}
			
			return {"success":False,"message":companyCheckResponse['message']}	
		else:
			return {"success":True,"data":tay_payer_details,"update":True}
	except Exception as e:
		print(e,"get tax payers")
		return {"success":False,"message":e}


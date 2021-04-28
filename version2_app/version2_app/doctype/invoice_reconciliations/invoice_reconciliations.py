# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
from datetime import date
import calendar
class InvoiceReconciliations(Document):
	pass

import frappe
import traceback
# import pandas as pd

@frappe.whitelist(allow_guest=True)
def invoicereconciliationcount(data):
	try:
		
		monthrange = calendar.monthrange(2021, int(data['month']))
		fromdate =data['year']+'-'+data['month']+'-01'
		todate = data['year']+'-'+data['month']+'-'+str(monthrange[1])
		outputdata=[]
		for each in range(1,monthrange[1]+1):
			if each<10:
				each = '0'+str(each)
			else:
				each = str(each)	
			print(data['year'],data['month'])
			indate = data['year']+'-'+data['month']+'-'+each
			getdata = frappe.db.get_list('Invoice Reconciliations',filters={'bill_generation_date':["between", [indate, indate]],'invoice_found':'No'},fields=['count(name) as count', 'bill_generation_date'],group_by='bill_generation_date')
			if len(getdata)==0:
				datecheck = frappe.db.get_list('Invoice Reconciliations',filters={'bill_generation_date':["between", [indate, indate]]})
				# print(datecheck,"daaaaaaa")
				if len(datecheck)==0:
					outputdata.append({'bill_generation_date':indate,"count":"No data Found"})
				else:
					outputdata.append({'bill_generation_date':indate,"count":0})
			else:
				outputdata.append(getdata[0])	
		return {"success":True,"data":outputdata}
	
	except Exception as e:
		print(traceback.print_exc())
		return {"status":False,"message":str(e)}   


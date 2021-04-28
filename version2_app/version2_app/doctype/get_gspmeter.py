
from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
# from datetime import date
import calendar
class InvoiceReconciliations(Document):
	pass

import frappe
import traceback
import datetime
from dateutil.relativedelta import relativedelta
# import pandas as pd

@frappe.whitelist(allow_guest=True)
def gspmeatering(data):
	try:
		date=datetime.datetime.today()
		outputdata=[]
		if data["range"]=="this week":
			start_day = (date - datetime.timedelta(days=date.weekday())).date().day
			end_day=date.day
		elif data["range"]== "last week":
			from_date = (date + datetime.timedelta(-date.weekday(), weeks=-1)).date()
			to_date = (date + datetime.timedelta(-date.weekday() - 1)).date()
			start_day = from_date.day
			end_day=to_date.day
		elif data["range"]=="this month":
			start_day=1
			end_day=date.day
		elif data["range"]=="last month":
			date=datetime.datetime.now()
			d = date - relativedelta(months=1)
			from_date = datetime.date(d.year, d.month, 1)
			today=date.today()
			to_date = datetime.date(today.year, today.month, 1) - relativedelta(days=1)
			start_day=from_date.day
			end_day=to_date.day
		for each in range(start_day,end_day+1):
			if each<10:
				each = '0'+str(each)
			else:
				each = str(each)
			if data["range"]=="last month":
				indate = str(date.year)+'-'+str(date.month-1)+'-'+each
			else:
				indate =str(date.year)+'-'+str(date.month)+'-'+each
			getdata = frappe.db.get_list('Gsp Metering',filters={'creation':["between", [indate, indate]]},fields=['count(name) as count',"tax_payer_details",'creation'],group_by='tax_payer_details')
			if len(getdata)==0:
				datecheck = frappe.db.get_list('Gsp Metering',filters={'creation':["between", [indate, indate]]})
				if len(datecheck)==0:
					outputdata.append({'creation':indate,"count":"No data Found"})
				else:
					outputdata.append({'creation':indate,"count":0})
			else:
				getdata[0]["creation"]=indate
				outputdata.append(getdata[0])	
		return {"success":True,"data":outputdata}
	
	except Exception as e:
		print(traceback.print_exc())
		return {"status":False,"message":str(e)}  







# import frappe,json
# # from __future__ import unicode_literals
# # import frappe
# from frappe.model.document import Document
# from datetime import date
# import calendar

# @frappe.whitelist(allow_guest=True)
# def getGsp(data):
# 	# doc = frappe.db.sql("""select * from `tabGsp Meteorites` where MONTH(creation)=04 """,as_dict=1)
# 	# return(doc)
# 	# if frappe.local.request.method=="POST":
# 	# 	data = json.loads(frappe.request.data)
# 	# 	print(data)
# 	# 	dateformat = '%Y-%m-%d'
# 	# 	# startdate = data["start_date"]
# 	# 	# print(startdate)
# 	# 	# enddate = data["end_date"]
# 	monthrange = calendar.monthrange(2021, int(data['month']))
# 	print("///////////////",monthrange)
# 	fromdate =data['year']+'-'+data['month']+'-01'
# 	todate = data['year']+'-'+data['month']+'-'+str(monthrange[1])
# 	outputdata=[]
# 	tax_payer_details=frappe.db.get_all('Gsp Meteorites',filters={'creation': ['between', (startdate,enddate)]},fields=['count(name) as count','tax_payer_details','creation'],group_by='tax_payer_details')
# 	generate_irn=frappe.db.get_all('Gsp Meteorites',filters={'creation': ['between', (startdate,enddate)]},fields=['count(name) as count','generate_irn','creation'],group_by='generate_irn')
# 	get_irn_details_by_doc=frappe.db.get_all('Gsp Meteorites',filters={'creation': ['between', (startdate,enddate)]},fields=['count(name) as count','get_irn_details_by_doc','creation'],group_by='get_irn_details_by_doc')
# 	login=frappe.db.get_all('Gsp Meteorites',filters={'creation': ['between', (startdate,enddate)]},fields=['count(name) as count','login','creation'],group_by='login')
# 	sync_gst_details = frappe.db.get_all('Gsp Meteorites',filters={'creation': ['between', (startdate,enddate)]},fields=['count(name) as count','sync_gst_details','creation'],group_by='sync_gst_details')
# 	invoice_by_irn = frappe.db.get_all('Gsp Meteorites',filters={'creation': ['between', (startdate,enddate)]},fields=['count(name) as count','invoice_by_irn','creation'],group_by='invoice_by_irn')
# 	cancel_irn = frappe.db.get_all('Gsp Meteorites',filters={'creation': ['between', (startdate,enddate)]},fields=['count(cancel_irn) as count','cancel_irn','creation'],group_by='cancel_irn')
# 	sql_filter = {"tax_payer_details":tax_payer_details,"generate_irn":generate_irn,"get_irn_details_by_doc":get_irn_details_by_doc,"sync_gst_details":sync_gst_details,"invoice_by_irn":invoice_by_irn,"cancel_irn":cancel_irn,"login":login}
# 	if sql_filter != []:
# 		return {"success":True,"data":sql_filter}
# 	else:
# 		return {"success":False,"message":"no data found"}

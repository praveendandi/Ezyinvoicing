import frappe
from frappe.utils import getdate, requests, json

@frappe.whitelist(allow_guest=True)
def getCreditnote():
    if frappe.local.request.method=="POST":
        data = json.loads(frappe.request.data)
        dateformat = '%Y-%m-%d'
        startdate = getdate(data["start_date"])
        enddate = getdate(data["end_date"])
        sql_filter=frappe.db.get_all('Credit Note Items',filters={'creation': ['between', (startdate,enddate)]},fields=['sac_code','sum(igst) as igst','sum(cgst) as cgst','sum(sgst) as sgst', 'sum(sgst+cgst+igst) as Total','creation'],group_by='sac_code')
        if sql_filter != []:
            return {"success":True,"data":sql_filter}
        else:
            return {"success":False,"message":"no data found"}

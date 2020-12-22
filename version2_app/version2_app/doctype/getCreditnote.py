import frappe
from frappe.utils import getdate, requests, json

@frappe.whitelist(allow_guest=True)
def getCreditnote():
    if frappe.local.request.method=="POST":
        data = json.loads(frappe.request.data)
        dateformat = '%Y-%m-%d'
        startdate = getdate(data["start_date"])
        enddate = getdate(data["end_date"])
        sql_filter=frappe.db.get_all('Items',filters={'item_mode':'Credit','creation': ['between', (startdate,enddate)]},fields=['sac_code','sum(-igst_amount) as igst','sum(-cgst_amount) as cgst','sum(-sgst_amount) as sgst', 'sum(-sgst_amount-cgst_amount-igst_amount) as Total','creation'],group_by='sac_code')
        if sql_filter != []:
            return {"success":True,"data":sql_filter}
        else:
            return {"success":False,"message":"no data found"}


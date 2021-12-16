import frappe
from frappe.utils import getdate
import requests,json,sys,traceback,os
@frappe.whitelist(allow_guest=True)
def getTotalamount():
    try:
        if frappe.local.request.method=="POST":
            data = json.loads(frappe.request.data)
            dateformat = '%Y-%m-%d'
            startdate = getdate(data["start_date"])
            enddate = getdate(data["end_date"])
            sql_filter=frappe.db.get_all('SAC HSN Tax Summaries',filters={'creation': ['between', (startdate,enddate)]},fields=['sac_hsn_code','sum(igst) as igst','sum(cgst) as cgst','sum(sgst) as sgst','sum(sgst+igst+cgst) as total_amount','creation'],group_by='sac_hsn_code')
            if sql_filter != []:
                return {"success":True,"data":sql_filter}
            else:
                return {"success":False,"message":"no data found"}
    except Exception as e:            
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing Hsn Amount","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))            
        return {"success":False, "message": str(e)}
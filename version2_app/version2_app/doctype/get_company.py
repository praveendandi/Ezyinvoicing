import frappe
import requests
import json
@frappe.whitelist(allow_guest=True)
def company_created(doc,method=None):
    doc = frappe.db.get_list('company',filters={"docstatus":0},fields=["name","company_name","company_code","phone_number","gst_number","provider","ip_address","port"])
    api="http://"+doc[0]["ip_address"]+":"+doc[0]["port"]+"/api/resource/Properties"
    adequare_doc=frappe.get_doc("GSP APIS",doc[0]["provider"])
    # print(adequare_doc.gsp_test_app_secret,adequare_doc.gsp_test_app_id,adequare_doc.gsp_prod_app_id,adequare_doc.gsp_prod_app_secret)
    insert_dict={"doctype":"Properties","property_name":doc[0]["company_name"],"property_code":doc[0]["company_code"],"contact_number":doc[0]["phone_number"],"gst_number":doc[0]["gst_number"],"gsp_provider":doc[0]["provider"],"api_key":adequare_doc.gsp_prod_app_secret,"api_secret":adequare_doc.gsp_prod_app_id,"gsp_test_app_id":adequare_doc.gsp_test_app_id,"gsp_test_app_secret":adequare_doc.gsp_test_app_secret}
    print(insert_dict)
    headers = {'content-type': 'application/json'}
    r = requests.post(api,headers=headers,json=insert_dict)


    # json_response = requests.post("https://gst.caratred.in/ezy/api/addJsonToGcb",headers=headers,json=b2c_data)
    print(r.text)        


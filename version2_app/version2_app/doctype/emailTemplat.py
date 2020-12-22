import requests
import random
import datetime
import json
import requests
import frappe
@frappe.whitelist(allow_guest=True)
def emailTemplate():
    data = json.loads(frappe.request.data)
    get_invoice = frappe.get_doc('Invoices',data['invoice_number'])
    obj = {}
    if get_invoice.invoice_type=="B2B" and get_invoice.irn_generated == "Success":
        get_invoiceDetails = {"invoice_number":get_invoice.invoice_number,"company":get_invoice.company,"irn_number":get_invoice.irn_number,"ack_no":get_invoice.ack_no,"ack_date":get_invoice.ack_date,"gst_number":get_invoice.gst_number}
        b2bsuccess = frappe.get_doc('Email Template',"B2B-Success")
        response_data = b2bsuccess.response
        rep=response_data.replace("invoice_number", get_invoice.invoice_number)
        re=rep.replace("company", get_invoice.company)
        irn_re=re.replace("irn_number",get_invoice.irn_number)
        ack_re=irn_re.replace("ack_no",get_invoice.ack_no)
        ack_date=ack_re.replace("ack_date",get_invoice.ack_date)
        gst_num=ack_date.replace("gst_number",get_invoice.gst_number)
        b2bsuccess.response=gst_num
        obj["val"] = b2bsuccess
        files=frappe.db.get_list('File',filters={'attached_to_name': ['=',data['invoice_number']]},fields=['name'])
        obj["attachments"] = [d['name'] for d in files]
        return(obj)


    elif get_invoice.invoice_type== "B2B" and get_invoice.irn_generated == "Pending":
        get_invoiceDetails = {"invoice_number":get_invoice.invoice_number,"company":get_invoice.company,"gst_number":get_invoice.gst_number}
        get_email_B2B_Pending = frappe.get_doc('Email Template',"B2B-Pending")
        b2bpending = frappe.get_doc('Email Template',"B2B-Pending")
        response_data = b2bpending.response
        rep=response_data.replace("invoice_number", get_invoice.invoice_number)
        re=rep.replace("gst_number", get_invoice.gst_number)
        replace_b2b=re.replace("company", get_invoice.company)  
        b2bpending.response= replace_b2b
        obj["val"] = b2bpending
        files=frappe.db.get_list('File',filters={'attached_to_name': ['=',data['invoice_number']]},fields=['name'])
        obj["attachments"] = [d['name'] for d in files]
        return(obj)


    elif get_invoice.invoice_type== "B2C":
        get_invoiceDetails = {"invoice_number":get_invoice.invoice_number,"company":get_invoice.company}
        b2csuccess = frappe.get_doc('Email Template',"B2C-Success")
        response_data = b2csuccess.response
        rep=response_data.replace("invoice_number", get_invoice.invoice_number)
        re=rep.replace("company", get_invoice.company)
        b2csuccess.response=re 
        obj["val"] = b2csuccess
        files=frappe.db.get_list('File',filters={'attached_to_name': ['=',data['invoice_number']]},fields=['name'])
        obj["attachments"] = [d['name'] for d in files]
        return(obj)
        
    

    else:
        return ({"success": False, "message": "Invoice Errored"})
  



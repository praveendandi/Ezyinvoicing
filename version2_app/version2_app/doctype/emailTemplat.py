import random
import datetime,os,sys,traceback
import json
import requests
import frappe
from frappe.core.doctype.communication.email import make

@frappe.whitelist(allow_guest=True)
def emailTemplate():
    try:
        data = json.loads(frappe.request.data)
        get_invoice = frappe.get_doc('Invoices',data['invoice_number'])
        obj = {}
        if get_invoice.invoice_type=="B2B" and get_invoice.irn_generated == "Success":
            get_invoiceDetails = {"invoice_number":get_invoice.invoice_number,"company":get_invoice.company,"irn_number":get_invoice.irn_number,"ack_no":get_invoice.ack_no,"ack_date":get_invoice.ack_date,"gst_number":get_invoice.gst_number}
            b2bsuccess = frappe.get_doc('Email Template',"B2B-Success")
            response_data = b2bsuccess.response
            rep=response_data.replace("invoice_number", get_invoice.invoice_number)
            re=rep.replace("company", get_invoice.company)
            if get_invoice.invoice_category != "Credit Invoice":
                irn_re=re.replace("irn_number",get_invoice.irn_number)
                ack_re=irn_re.replace("ack_no",get_invoice.ack_no)
                ack_date=ack_re.replace("ack_date",get_invoice.ack_date)
            if get_invoice.invoice_category == "Credit Invoice":
                irn_re=re.replace("irn_number",get_invoice.credit_irn_number)
                ack_re=irn_re.replace("ack_no",get_invoice.credit_ack_no)
                ack_date=ack_re.replace("ack_date",get_invoice.credit_ack_date)
            gst_num=ack_date.replace("gst_number",get_invoice.gst_number)
            b2bsuccess.response=gst_num
            obj["val"] = b2bsuccess
            # files=frappe.db.get_list('File',filters={'attached_to_name': ['=',data['invoice_number']]},fields=['name'])
            # obj["attachments"] = [d['name'] for d in files]
            obj['attachments'] = data['templateFiles']
            if len(data['templateFiles'])==0:
                files=frappe.db.get_list('File',filters={'file_url': ['=',get_invoice.invoice_file]},fields=['name'])
                obj["attachments"] = [d['name'] for d in files]

            # print(obj['val']['response'])
            # print(obj['val'].__dict__['response'].replace("{{",""))
            obj['val'].__dict__['response'] = obj['val'].__dict__['response'].replace("{{","")
            obj['val'].__dict__['response'] = obj['val'].__dict__['response'].replace("}}","")
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
            obj['val'].__dict__['response'] = obj['val'].__dict__['response'].replace("{{","")
            obj['val'].__dict__['response'] = obj['val'].__dict__['response'].replace("}}","")
            return(obj)


        elif get_invoice.invoice_type== "B2C":
            get_invoiceDetails = {"invoice_number":get_invoice.invoice_number,"company":get_invoice.company}
            b2csuccess = frappe.get_doc('Email Template',"B2C-Success")
            response_data = b2csuccess.response
            rep=response_data.replace("invoice_number", get_invoice.invoice_number)
            re=rep.replace("company", get_invoice.company)
            b2csuccess.response=re 
            obj["val"] = b2csuccess
            # files=frappe.db.get_list('File',filters={'attached_to_name': ['=',data['invoice_number']]},fields=['name'])
            # obj["attachments"] = [d['name'] for d in files]
            obj['attachments'] = data['templateFiles']
            if len(data['templateFiles'])==0:
                files=frappe.db.get_list('File',filters={'file_url': ['=',get_invoice.invoice_file]},fields=['name'])
                obj["attachments"] = [d['name'] for d in files]

            obj['val'].__dict__['response'] = obj['val'].__dict__['response'].replace("{{","")
            obj['val'].__dict__['response'] = obj['val'].__dict__['response'].replace("}}","")
            return(obj)
            
        

        else:
            return ({"success": False, "message": "Invoice Errored"})
  
    except Exception as e:
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing emailTemplate","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return ({"success": False, "message":str(e)})

@frappe.whitelist(allow_guest=True)
def send_email():
    """send email with payment link"""
    try:
        # send_mail = frappe.sendmail(recipients=["ganesh@caratred.com"], subject="Invoice Reg.",
        #     message="sample", attachments=[frappe.attach_print(doctype="File",name="ab5aba0184")])
        # print(send_mail,"//////////")
        pdffilename = frappe.get_doc("File","ab5aba0184")
        
        frappe.sendmail(
            recipients = "info@caratred.com",
            cc = '',
            subject = 'Sample',
            content = 'Message',
            reference_doctype = 'File',
            reference_name = 'ab5aba0184',
            attachments=[frappe.attach_print(doctype="File",name="ab5aba0184",file_name=pdffilename.file_name,print_letterhead=True)],
            now = True
        )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing send_email","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(str(e))
        return{"success":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)
def send_mail_files(data):
    try:
        obj = {"email":""}
        get_doc = frappe.get_doc(data["doctype"],data["name"])
        if data["doctype"] == "Invoices":
            if get_doc.confirmation_number != "":
                obj["email"] = frappe.db.get_value("Arrival Information",get_doc.confirmation_number,["guest_email_address"])
        b2csuccess = frappe.get_doc('Email Template',"Scan Ezy")
        obj["val"] = b2csuccess
        files=frappe.db.get_list('File',filters={'file_url': ['=',data["attachments"]]},fields=['name'])
        obj["attachments"] = [d['name'] for d in files]
        return {"success": True, "obj":obj}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing send_email_files","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(str(e))
        return{"success":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)    
def email_logs():
    try:
        data = frappe.db.get_all("Email Queue",fields=["sender","status","name","creation"])
        for each in data:
            each["recipient"]=frappe.db.get_value("Email Queue Recipient",{"parent":each["name"]},"recipient")
        return {"success": True, "data":data}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing email_logs","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(str(e))
        return{"success":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)    
def email_push_tab():
    try:
        data = json.loads(frappe.request.data)
        data = data["data"]
        print(data,"===========================================")
        get_doc = frappe.get_doc(data["doctype"],data["name"])
        b2csuccess = frappe.get_doc('Email Template',"Scan Ezy")
        files=frappe.db.get_list('File',filters={'file_url': ['=',data["attachments"]]},fields=['name'])
        attachments = [d['name'] for d in files]
        response = make(recipients = data["email"],
            # cc = '',
            subject = b2csuccess.subject,
            content = b2csuccess.response,
            doctype = data["doctype"],
            name = data["name"],
            attachments = attachments,
            send_email=1
        )
        return {"success":True,"message":"Mail sent successfully"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing email_logs","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(str(e))
        return{"success":False,"message":str(e)}
import random
import datetime,os,sys,traceback
import json
import requests
import frappe
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
def send_email(data):
    """send email with payment link"""
    try:
        # send_mail = frappe.sendmail(recipients=["ganesh@caratred.com"], subject="Invoice Reg.",
        #     message="sample", attachments=[frappe.attach_print(doctype="File",name="ab5aba0184")])
        # print(send_mail,"//////////")
        folder_path = frappe.utils.get_bench_path()
        companyCheckResponse = frappe.get_last_doc('company')
        site_folder_path = companyCheckResponse.site_name
        if "private" in data["attachments"]:
            file_path = folder_path+'/sites/'+site_folder_path+data["attachments"]
        else:
            file_path = folder_path+'/sites/'+site_folder_path+"/public"+data["attachments"]
        get_file = frappe.db.get_value("File",{"file_name":data["attachments"].replace("/private/files/","").replace("/files/","")})
        pdffilename = frappe.get_doc("File",get_file)
        with open(file_path, 'r') as f:
	        content = f.read()
        frappe.sendmail(
            recipients = data["recipients"],
            cc = '',
            subject = data["subject"],
            content = data["content"],
            reference_doctype = 'Redg Card',
            read_receipt = data["read_receipt"],
            reference_name = data["name"],
            attachments=[{'fname': data["attachments"].replace("/private/files/","").replace("/files/",""),'fcontent': content}],
            now = True
        )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing send_email","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(str(e))
        return{"success":False,"message":str(e)}

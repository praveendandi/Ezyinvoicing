import frappe
from invoice_sync.invoice_sync.doctype.sync_logs.customer_sync_util import check_customer_exist
from version2_app.events import invoice_created
from invoice_sync.invoice_sync.doctype.sync_logs.sync_logs import get_company_details
# @frappe.whitelist()
# def taxpayerdetail(doc,method=None):
#     frappe.db.set_value('TaxPayerDetail',doc.name,{'synced_date':None,'synced_to_erp': 0})
#     frappe.db.commit()
from invoice_sync.invoice_sync.doctype.sync_logs.customer_sync_util import check_customer_exist, create_customer, create_adress, get_state_name_by_state_code, check_address_exist
from invoice_sync.invoice_sync.doctype.sync_logs.items_sync_util import check_item_exist, create_item
from invoice_sync.invoice_sync.doctype.sync_logs.invoices_sync_util import create_invoice
from invoice_sync.invoice_sync.doctype.sync_logs.sync_logs import create_customer_address
from datetime import date, datetime
from invoice_sync.invoice_sync.doctype.sync_logs.sync_logs import sync_taxpayer_details
from frappe.utils.background_jobs import enqueue
from invoice_sync.invoice_sync.doctype.sync_logs.sync_logs import sync_items
from invoice_sync.invoice_sync.doctype.sync_logs.sync_logs import sync_invoices


api_list = {
    "get_customer": "/api/method/frappe.desk.form.load.getdoc?doctype=Customer&name=",
    "get_customer_gst": '/api/resource/Customer?filters=[["Customer","gstin","=","{gst_place_holder}"]]&fields=["name","gstin"]',
    "create_customer": "/api/resource/Customer",
    "create_address": "/api/resource/Address",
    "get_address": "/api/method/frappe.desk.form.load.getdoc?doctype=Address&name=",
    "get_address_gst": '/api/resource/Address?filters=[["Address","gstin","=","{gst_place_holder}"]]&fields=["name","gstin","gst_state_number","gst_state"]',
    "get_item": "/api/method/frappe.desk.form.load.getdoc?doctype=Item&name=",
    "create_item": "/api/resource/Item",
    "create_invoice": "/api/resource/Sales Invoice",
    "e_invoice_invoice": "/api/resource/e-Invoice Log",
}


@frappe.whitelist()
def invoices(doc,method=None):
    taxpayer_details = frappe.db.get_all('TaxPayerDetail', {'synced_to_erp': 0}, ['gst_number', 'legal_name', "email", "address_1", "address_2", "location",
                                                                                     "pincode", "gst_status", "tax_type", "trade_name", "phone_number", "state_code", "address_floor_number", "address_street", "block_status", "synced_to_erp"])
    print(taxpayer_details,"..........")
    company = get_company_details()
    config_details = frappe.get_doc('Sync Configrations')
   
    url = config_details.host
    if config_details.port != 0:
        url = config_details.host+':'+str(config_details.port)
    headers = {
        "content-type": "application/json",
        'Authorization': "token "+config_details.login_token+":"+config_details.login_secret,
    }
    payer_count = 0
    success_count = 0
    if doc.invoice_type == "B2B":
        print("-------------------")
        for payer in taxpayer_details:
            # if payer["gst_number"] == "33AADCM5146R1CD":
            #     continue
            # check customer exist or not
            check_customer_resp = check_customer_exist(
                url+api_list['get_customer']+payer['legal_name']+'-'+payer['gst_number'], headers)
            # url+api_list['get_customer']+payer['legal_name']+payer['gst_number'][-2:], headers)
            print(check_customer_resp, "customer", payer['gst_number'])
            if "message" not in check_customer_resp:
                error_log = frappe.get_doc({
                    "error": "Duplicate taxpayer" if "exception" not in check_customer_resp else check_customer_resp["exception"],
                    "customer": payer['gst_number'],
                    "doctype": "Errors",
                    "parent": doc.gst_number,
                    "parentfield": "error",
                    "parenttype": "Sync Logs"
                })
                error_log.insert()
                frappe.db.commit()
                payer_count+=1
                frappe.publish_realtime("custom_socket", {'message':'Taxpayer Sync','type':"Sync Taxpayer","gstin":payer['gst_number'],"company":company.name, "count":len(taxpayer_details), "taxpayer_count": payer_count})
                # check address
                if "exception" in check_customer_resp:
                    continue
                address_name = check_customer_resp['docs'][0]['name']+'-Billing'
                check_address_resp = check_address_exist(
                    url+api_list['get_address']+address_name, headers)
                if "message" not in check_address_resp:
                    print("duplicate address")
                    frappe.db.set_value(
                        'TaxPayerDetail', payer['gst_number'], 'synced_to_erp', 1)
                else:
                    cutomer_name = check_customer_resp['docs'][0]['name']
                    state = get_state_name_by_state_code(payer['state_code']) if get_state_name_by_state_code(
                        payer['state_code']) != False else ''
                    if state != '':
                        create_customer_address(
                            payer, cutomer_name, url+api_list["create_address"], headers)
                    else:
                        print("no state")
                        doc = frappe.get_doc('Sync Logs', doc.gst_number)
                        print(doc.name)
                        doc.append("error", {
                            "error": "No Customer Found",
                            "customer": payer['gst_number']
                        })
                        doc.insert()
                        frappe.db.commit()
            else:
                # create customer[]
                # ['Registered Composition',
                # "Registered Regular",
                # "Unregistered",
                # "SEZ",
                # "Overseas",
                # "Deemed Export",
                # "UIN Holders",
                # "Tax Deductor"]

                # SED REG CTP SEZ ISD EMB COM
                #
                gst_category = "Registered Regular"
                if payer['tax_type'] == "SEZ":
                    gst_category = "SEZ"
                elif payer['tax_type'] == "COM":
                    gst_category = "Registered Composition"
                elif payer['tax_type'] == 'EMB':
                    gst_category = "UIN Holders"
                elif payer['tax_type'] == 'UNB':
                    gst_category = "UIN Holders"
                elif payer['tax_type'] == 'TDS':
                    gst_category = "Tax Deductor"
                elif payer['tax_type'] == 'TCS':
                    gst_category = ""

                customer = {
                    "doctype": "Customer",
                    "customer_type": "Company",
                    "gst_category": "Unregistered",
                    "customer_name": payer['legal_name']+'-'+payer['gst_number'],
                    # "customer_name": payer['legal_name'],
                    "customer_group": 'Commercial',
                    "territory": "India",
                    "gst_category": gst_category,
                    "gstin": payer['gst_number'],
                    # "payment_terms": "dummy"
                }
                create_customer_resp = create_customer(
                    url+api_list["create_customer"], headers, customer)

                # create address
                # have to check customer object in different secnirio
                cutomer_name = create_customer_resp['data']['name']
                state = get_state_name_by_state_code(payer['state_code']) if get_state_name_by_state_code(
                    payer['state_code']) != False else ''
                if state != '':
                    create_customer_address(
                        payer, cutomer_name, url+api_list["create_address"], headers)
                    today = date.today()
                    frappe.db.set_value("TaxPayerDetail", payer['gst_number'], {"synced_to_erp": 1, "synced_date": str(today)})
                    frappe.db.commit()
                    payer_count+=1
                    frappe.publish_realtime("custom_socket", {'message':'Taxpayer Sync','type':"Sync Taxpayer","gstin":payer['gst_number'],"company":company.name, "count":len(taxpayer_details), "taxpayer_count": payer_count})
                    success_count+=1
                else:
                    error_log = frappe.get_doc({
                        "error": "No Customer Found",
                        "customer": payer['gst_number'],
                        "doctype": "Errors",
                        "parent": doc.gst_number,
                        "parentfield": "error",
                        "parenttype": "Sync Logs"
                    })
                    error_log.insert()
                    frappe.db.commit()
                    payer_count+=1
                    frappe.publish_realtime("custom_socket", {'message':'Taxpayer Sync','type':"Sync Taxpayer","gstin":payer['gst_number'],"company":company.name, "count":len(taxpayer_details), "taxpayer_count": payer_count})

            # print(create_adress)
    else:
    # b2c customer
        company = get_company_details()
        customer = {
            "doctype": "Customer",
            "customer_type": "Company",
            "customer_name": "Unregister"+'-'+company.abbr,
            # "customer_name": payer['legal_name'],
            "customer_group": 'Commercial',
            "territory": "India",
            "gst_category": "Unregistered",
            # "gstin": payer['gst_number'],
            # "payment_terms": "dummy"
        }
        create_customer_resp = create_customer(
            url+api_list["create_customer"], headers, customer)

        # create address
        # have to check customer object in different secnirio
        cutomer_name = create_customer_resp['data']['name']
        payer = {
            "tax_type": "Unregistered",
            "gst_number": "",
            "email": company.email,
            "phone_number": company.phone_number,
            "location": company.location,
            "address_1": company.address_1,
            "address_2": company.address_2,
            "state_code": company.state_code,
            "pincode": company.pincode

        }
        create_customer_address(
            payer, cutomer_name, url+api_list["create_address"], headers)
        if success_count == 0:
            error_data = {"status": "Error", "success_records_count": success_count, "message": "No taxpayer upload to ezygst"}
        elif success_count != len(taxpayer_details):
            error_data = {"status": "Partial Success", "success_records_count": success_count}
        else:
            error_data = {"status": "Success", "success_records_count": success_count}
        frappe.db.set_value("Sync Logs",doc.gst_number, error_data)
        frappe.db.commit()
        return {"success": True, "message": "Items uploaded"}
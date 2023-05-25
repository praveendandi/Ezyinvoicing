import frappe
import json
import requests

@frappe.whitelist()
def get_total_dashboard_count_sync_history(month=None,year=None):
    company = frappe.get_last_doc("company")
    print(company)
    total_b2b_invoices_count = frappe.db.sql("""select count(name) as total_invoices_b2b from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2B' and irn_generated='Success'""".format(
                month, year
            ),
            as_dict=1,
        )
    total_b2c_invoices_count = frappe.db.sql("""select count(name) as total_invoices_b2c from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2C' and irn_generated='Success'""".format(
                month, year
            ),
            as_dict=1,
        )
    total_b2b_invoices_count_pending = frappe.db.sql("""select count(name) as total_invoices_b2b_pending from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2B' and irn_generated='Pending' """.format(
                month, year
            ),
            as_dict=1,
        )
    total_b2b_invoices_count_error = frappe.db.sql("""select count(name) as total_invoices_b2b_error from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2B' and irn_generated="Error" """.format(
                month, year
            ),
            as_dict=1,
        )
    total_b2c_invoices_count_pending = frappe.db.sql("""select count(name) as total_invoices_b2c_pending from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2C' and irn_generated='Pending' """.format(
                month, year
            ),
            as_dict=1,
        )
    total_b2c_invoices_count_error = frappe.db.sql("""select count(name) as total_invoices_b2c_error from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2C' and irn_generated="Error" """.format(
                month, year
            ),
            as_dict=1,
        )
    total_b2b_invoices_count_not_synced = frappe.db.sql("""select count(name) as total_b2b_invoices_not_synced from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2B' and irn_generated='Success' and synced_to_erp=0""".format(
                month, year
            ),
            as_dict=1,
        )
    total_b2b_invoices_count_synced = frappe.db.sql("""select count(name) as total_b2b_invoices_synced from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2B' and irn_generated='Success' and synced_to_erp=1""".format(
                month, year
            ),
            as_dict=1,
        )
    total_b2c_invoices_count_not_synced = frappe.db.sql("""select count(name) as total_b2c_invoices_not_synced from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2C' and irn_generated='Success' and synced_to_erp=0""".format(
                month, year
            ),
            as_dict=1,
        )
    total_b2c_invoices_count_synced = frappe.db.sql("""select count(name) as total_b2c_invoices_synced from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2C' and irn_generated='Success' and synced_to_erp=1""".format(
                month, year
            ),
            as_dict=1,
        )
    total_credit_invoices_reg = frappe.db.sql("""select count(name) as total_credit_invoices_reg from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2B' and invoice_category='Credit Invoice' and irn_generated='Success'""".format(
                month, year
            ),
            as_dict=1,
        )
    total_credit_invoices_reg_synced = frappe.db.sql("""select count(name) as total_credit_invoices_reg_synced from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2B' and invoice_category='Credit Invoice' and irn_generated='Success' and synced_to_erp=1""".format(
                month, year
            ),
            as_dict=1,
        )
    total_credit_invoices_reg_unsynced = frappe.db.sql("""select count(name) as total_credit_invoices_reg_unsynced from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2B' and invoice_category='Credit Invoice' and irn_generated='Success' and synced_to_erp=0""".format(
                month, year
            ),
            as_dict=1,
        )
    total_credit_invoices_unreg_synced = frappe.db.sql("""select count(name) as total_credit_invoices_unreg_synced from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2C' and invoice_category='Credit Invoice' and irn_generated='Success' and synced_to_erp=1""".format(
                month, year
            ),
            as_dict=1,
        )
    total_credit_invoices_unreg_unsynced = frappe.db.sql("""select count(name) as total_credit_invoices_unreg_unsynced from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2C' and invoice_category='Credit Invoice' and irn_generated='Success' and synced_to_erp=0""".format(
                month, year
            ),
            as_dict=1,
        )
    
    total_credit_invoices_reg_pending = frappe.db.sql("""select count(name) as total_credit_invoices_reg_pending from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2B' and invoice_category='Credit Invoice' and irn_generated='Pending'""".format(
                month, year
            ),
            as_dict=1,
        )
    total_credit_invoices_reg_error = frappe.db.sql("""select count(name) as total_credit_invoices_reg_error from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2B' and invoice_category='Credit Invoice' and irn_generated='Error'""".format(
                month, year
            ),
            as_dict=1,
        )
    total_credit_invoices_unreg_pending = frappe.db.sql("""select count(name) as total_credit_invoices_unreg_pending from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2C' and invoice_category='Credit Invoice' and irn_generated='Pending'""".format(
                month, year
            ),
            as_dict=1,
        )
    total_credit_invoices_unreg_error = frappe.db.sql("""select count(name) as total_credit_invoices_unreg_error from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2C' and invoice_category='Credit Invoice' and irn_generated='Error'""".format(
                month, year
            ),
            as_dict=1,
        )
    total_credit_invoices_unreg = frappe.db.sql("""select count(name) as total_credit_invoices_unreg from `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={} and invoice_type='B2C' and invoice_category='Credit Invoice' and irn_generated='Success'""".format(
                month, year
            ),
            as_dict=1,
        )
    sync_history = {}
    sync_history["B2B Success"]=total_b2b_invoices_count[0]['total_invoices_b2b']
    sync_history["B2B Synced"]=total_b2b_invoices_count_synced[0]['total_b2b_invoices_synced']
    sync_history["B2B NotSynced"]=total_b2b_invoices_count_not_synced[0]['total_b2b_invoices_not_synced']
    sync_history["B2B Pending"]=total_b2b_invoices_count_pending[0]['total_invoices_b2b_pending']
    sync_history["B2B Error"]=total_b2b_invoices_count_error[0]['total_invoices_b2b_error']
    sync_history["B2C Success"]=total_b2c_invoices_count[0]['total_invoices_b2c']
    sync_history["B2C Synced"]=total_b2c_invoices_count_synced[0]['total_b2c_invoices_synced']
    sync_history["B2C NotSynced"]=total_b2c_invoices_count_not_synced[0]['total_b2c_invoices_not_synced']
    sync_history["B2C Pending"]=total_b2c_invoices_count_pending[0]['total_invoices_b2c_pending']
    sync_history["B2C Error"]=total_b2c_invoices_count_error[0]['total_invoices_b2c_error']
    sync_history["CreditNote(Registered) Success"]=total_credit_invoices_reg[0]['total_credit_invoices_reg']
    sync_history["CreditNote(Registered) Synced"]=total_credit_invoices_reg_synced[0]['total_credit_invoices_reg_synced']
    sync_history["CreditNote(Registered) NotSynced"]=total_credit_invoices_unreg_synced[0]['total_credit_invoices_unreg_synced']
    sync_history["CreditNote(Registered) Error"]=total_credit_invoices_reg_pending[0]['total_credit_invoices_reg_pending']
    sync_history["CreditNote(Registered) Pending"]=total_credit_invoices_reg_error[0]['total_credit_invoices_reg_error']
    sync_history["CreditNote(UnRegistered) Success"]=total_credit_invoices_unreg[0]['total_credit_invoices_unreg']
    sync_history["CreditNote(UnRegistered) Synced"]=total_credit_invoices_unreg_synced[0]['total_credit_invoices_unreg_synced']
    sync_history["CreditNote(UnRegistered) NotSynced"]=total_credit_invoices_unreg_unsynced[0]['total_credit_invoices_unreg_unsynced']
    sync_history["CreditNote(UnRegistered) Pending"]=total_credit_invoices_unreg_pending[0]['total_credit_invoices_unreg_pending']
    sync_history["CreditNote(UnRegistered) Error"]=total_credit_invoices_unreg_error[0]['total_credit_invoices_unreg_error']
    sync_history["Total Success Invoices"]=sync_history["B2B Success"]+sync_history["B2C Success"]+sync_history["CreditNote(Registered) Success"]+sync_history["CreditNote(UnRegistered) Success"]
    sync_history["Total Synced Invoices"] = sync_history["B2B Synced"]+sync_history["B2C Synced"]+sync_history["CreditNote(Registered) Synced"]+sync_history["CreditNote(UnRegistered) Synced"]
    sync_history["Total NotSynced Invoices"]= sync_history["B2B NotSynced"]+sync_history["B2C NotSynced"]+sync_history["CreditNote(Registered) NotSynced"]+sync_history["CreditNote(UnRegistered) NotSynced"]
    sync_history["Total Pending Invoices"] = sync_history["B2B Pending"]+sync_history["B2C Pending"]+sync_history["CreditNote(Registered) Pending"]+sync_history["CreditNote(UnRegistered) Pending"]
    sync_history["Total Error Invoices"] = sync_history["B2B Error"]+sync_history["B2C Error"]+sync_history["CreditNote(Registered) Error"]+sync_history["CreditNote(UnRegistered) Error"]
    # sync_history_payload = {'doctype': 'EzyInvoice Status',"company":company.company_name,"business_unit":company.company_code,"status_in_json":sync_history,"period":month+year}
    # headers = {"content-type": "application/json"}
    # post_data = requests.post(
    #                 "http://192.168.29.38:8000"
    #                 + "/api/resource/EzyInvoice Status",
    #                 headers=headers,
    #                 json=sync_history_payload,
    #                 verify=False,
    #             )
    # print(post_data.text,"///////////")
    sync_history_invoices = {"Invoice Data":sync_history}
    print(sync_history_invoices,"/////////////////")
import frappe



@frappe.whitelist(allow_guest=True)
def taxpayerdetail(doc,method=None):
    frappe.db.set_value('TaxPayerDetail',doc.name,{'synced_date':None,'synced_to_erp': 0})
    frappe.db.commit()

@frappe.whitelist(allow_guest=True)
def invoices(doc,method=None):
    frappe.db.set_value('TaxPayerDetail',doc.name,{'synced_date':None,'synced_to_erp': 0})
    frappe.db.commit()

@frappe.whitelist(allow_guest=True)
def sac_hsn_code(doc,method=None):
    frappe.db.set_value('TaxPayerDetail',doc.name,{'synced_date':None,'synced_to_erp': 0})
    frappe.db.commit()
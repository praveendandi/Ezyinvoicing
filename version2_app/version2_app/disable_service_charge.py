import frappe
import sys

@frappe.whitelist()
def disable_service_charge():
    try:
        sac_list = frappe.db.get_list("SAC HSN CODES",fields=["name","service_charge","state_cess_rate"])
        for each in sac_list:
            if each['service_charge']  == "Yes":
                frappe.db.set_value("SAC HSN CODES",each["name"],{"service_charge":"No"})
                frappe.db.commit()

            if each['state_cess_rate'] != 0.0:
                frappe.db.set_value("SAC HSN CODES",each["name"],{"state_cess_rate":0.0})
                frappe.db.commit()
        return {"success":True, "message":"Updated Successfull"}      
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("disable_service_charge",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}

    

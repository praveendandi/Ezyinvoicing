import frappe


@frappe.whitelist(allow_guest= True)
def disable_service_charge():
    sac_list = frappe.db.get_list("SAC HSN CODES",fields=["service_charge","state_cess_rate"])
    print(sac_list,"???????????")
    for each in sac_list:
        


        # updatesac = frappe.db.sql("""update tabSAC HSN CODES set service_charge ='No' where service_charge ='Yes'""")
        # frappe.db.commit()
        # return {"success":True,"message":"Successfully Updated"}
import frappe
import pandas as pd
import os
import sys
import requests
from frappe.utils import cstr, get_site_name
from urllib.parse import urljoin
from urllib.request import pathname2url
import time

@frappe.whitelist()
def get_all_taxpayer_details():
    try:
        site_name = frappe.utils.cstr(frappe.local.site)
        folder_path = frappe.utils.get_bench_path()
        taxpayer_details = frappe.db.get_list('TaxPayerDetail', ["gst_number", "legal_name", "trade_name", "address_1", "address_2", "location", "pincode", "gst_status", "tax_type", "state_code", "status"])
        convert_df = pd.DataFrame.from_records(taxpayer_details)
        fileName = "Taxpayer_Details".replace(" ","")

        cvs_file_path = (folder_path+ "/sites/"+ site_name)

        epoch = str(round(time.time() * 1000))

        file_path = f'/files/{fileName}{epoch}.csv'

        output_file_path = cvs_file_path + "/public"+file_path

        convert_df.to_csv(output_file_path,index=False,columns=convert_df)

        return {"success":True,"message": "Download successfully","file_path":file_path}   
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("get_all_taxpayer_details",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}



@frappe.whitelist()
def get_all_sac_code_details():
    try:
        site_name = frappe.utils.cstr(frappe.local.site)
        folder_path = frappe.utils.get_bench_path()
        sac_details = frappe.db.get_list('SAC HSN CODES', ["description","taxble","sgst","cgst","igst","net","code","type","status","company","transactioncode","state_cess_rate","central_cess_rate","vat_rate","service_charge","accommodation_slab","one_sc_applies_to_all","service_charge_rate","ignore","service_charge_net","service_charge_tax_applies","sc_gst_tax_rate","sc_sac_code","exempted","sac_index","ignore_non_taxable_items","bulk_upload_service_charge","disable_cess_for_sc","disable_vat_for_sc","category","is_service_charge_item","synced_to_erp","synced_date"])
        convert_df = pd.DataFrame.from_records(sac_details)
        convert_df.rename(columns={"description": "Description","taxble":"Taxble","sgst":"SGST","cgst":"CGST","igst":"IGST","code":"Code","type":"Type","status":"Status","company":"Company","net":"Net","transactioncode":"TransactionCode","state_cess_rate":"State Cess Rate","central_cess_rate":"Central Cess Rate","vat_rate":"Vat Rate","service_charge":"Service Charge","accommodation_slab":" Accommodation Slab","one_sc_applies_to_all":"One SC Applies To All","service_charge_rate":"Service Charge Rate","ignore":"Ignore","service_charge_net":"Service Charge Net","service_charge_tax_applies":"Service Charge Tax Applies","sc_gst_tax_rate":"SC GST Tax Rate","sc_sac_code":"SC SAC Code","exempted":"Exempted","sac_index":"SAC Index","ignore_non_taxable_items":"Ignore Non Taxable Items","bulk_upload_service_charge":"Bulk Upload Service charge","disable_cess_for_sc":"Disable Cess For SC","disable_vat_for_sc":"Disable Vat For SC","category":"Category","is_service_charge_item":"Is Service Charge Item","synced_to_erp":"Synced to ERP","synced_date":"Synced Date"}, inplace=True)
       
        fileName = "SAC_HSN_CODES".replace(" ","")

        cvs_file_path = (folder_path+ "/sites/"+ site_name)

        epoch = str(round(time.time() * 1000))

        file_path = f'/files/{fileName}{epoch}.csv'

        output_file_path = cvs_file_path + "/public"+file_path

        convert_df.to_csv(output_file_path,index=False,columns=convert_df)

        return {"success":True,"message": "Download successfully","file_path": file_path}
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()

        frappe.log_error("get_all_sac_code_details",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}
    

@frappe.whitelist()
def get_all_payment_details():
    try:
        site_name = frappe.utils.cstr(frappe.local.site)
        folder_path = frappe.utils.get_bench_path()
        sac_details = frappe.db.get_list('Payment Types', ["payment_type", "Status", "Company"])
        convert_df = pd.DataFrame.from_records(sac_details)
        
        convert_df.rename(columns={"payment_type": "Payment Type", "Status": "Status", "Company": "Company"}, inplace=True)

        fileName = "Payment_Types".replace(" ","")

        cvs_file_path = (folder_path+ "/sites/"+ site_name)

        epoch = str(round(time.time() * 1000))

        file_path = f'/files/{fileName}{epoch}.csv'

        output_file_path = cvs_file_path + "/public"+file_path

        convert_df.to_csv(output_file_path,index=False,columns=convert_df)

        return {"success":True,"message": "Download successfully","file_path":file_path}

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("get_all_payment_details",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}
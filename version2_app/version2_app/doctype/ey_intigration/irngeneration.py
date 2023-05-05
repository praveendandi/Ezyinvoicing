import frappe
import requests
import sys
import random
import traceback
# from frappe.utils import logger
from version2_app.version2_app.doctype.ey_intigration.api_urls import test_irn,prod_irn


def get_return_period_from_invoice_date(inv_date):
    try:
        return inv_date.split('/')[1]+inv_date.split('/')[2]
    except Exception as e:
        print(e)

def ey_generate_einvoice(gst_data, gsp, company, invoice_number):
    try:
        # print(gst_data)
        if gst_data['DocDtls']['Typ'] == 'INV':
            doc_type = 'INV'
        elif gst_data['DocDtls']['Typ'] == 'DBN':
            doc_type = 'DR'
        elif gst_data['DocDtls']['Typ'] == 'CRN':
            doc_type = 'CR'
        print(gst_data['BuyerDtls'])
        if gst_data['TranDtls']['SupTyp'] == 'B2B':
            gst_data['TranDtls']['SupTyp'] = 'TAX'
        req=[
        {
            "returnPeriod": get_return_period_from_invoice_date(gst_data['DocDtls']['Dt']),
            "suppGstin": company.gst_number,
            "docType": doc_type,
            "docNo": invoice_number,
            "docDate": gst_data['DocDtls']['Dt'].replace('/','-'),
            "custGstin": gst_data['BuyerDtls']['Gstin'],
            "custOrSupName": gst_data['BuyerDtls']['LglNm'],
            "custTradeName": gst_data['BuyerDtls']['TrdNm'],
            "custOrSupAddr1":  gst_data['BuyerDtls']['Addr1'],
            "custOrSupAddr2":  gst_data['BuyerDtls']['Addr2'],
            "custOrSupAddr4": gst_data['BuyerDtls']['Loc'],
            # "billToState": company.state_code,
            "billToState": gst_data['BuyerDtls']['Stcd'],
            "shipToState": company.state_code,
            "pos": company.state_code,
            "sec7OfIgstFlag": gst_data['TranDtls']['IgstOnIntra'],
            "reverseCharge": gst_data['TranDtls']['RegRev'],
            "autoPopToRefundFlag": "N",
            "accVoucherNo": gst_data['TranDtls']['TaxSch'],
            "accVoucherDate": "2021-05-05",
            "taxScheme": gst_data['TranDtls']['SupTyp'],
            "docCat": "REG",
            "supTradeName": gst_data['SellerDtls']['TrdNm'],
            "supLegalName": gst_data['SellerDtls']['LglNm'],
            "supBuildingNo": gst_data['SellerDtls']['Addr1'],
            "supBuildingName": gst_data['SellerDtls']['Addr2'],
            "supLocation": company.location,
            "supPincode": company.pincode,
            "supStateCode": company.state_code,
            "custPincode": gst_data['BuyerDtls']['Pin'],
            "roundOff":gst_data['ValDtls']['RndOffAmt'],
            # "dispatcherGstin": "29AAAPH9357H000",
            # "dispatcherTradeName": gst_data['SellerDtls']['TrdNm'],
            # "dispatcherBuildingNo": gst_data['SellerDtls']['Addr1'],
            # "dispatcherLocation": "Bangalore",
            # "dispatcherPincode": "560079",
            # "dispatcherStateCode": "29",
            # "shipToGstin": "08ABMPL5333Q1ZZ ",
            # "shipToLegalName": "3S Technologies & Automation Pvt333",
            # "shipToBuildingNo": "No.2, 100 Feet",
            # "shipToLocation": "Bangalore",
            # "shipToPincode": "302001",
            "invAssessableAmt": gst_data['ValDtls']['AssVal'],
            "invValueFc":gst_data['ValDtls']['TotInvValFc'],
            "invIgstAmt": gst_data['ValDtls']['IgstVal'],
            "invOtherCharges": gst_data['ValDtls']['OthChrg'],
            "invCgstAmt": gst_data['ValDtls']['CgstVal'],
            "invSgstAmt": gst_data['ValDtls']['SgstVal'],
            "invCessAdvaloremAmt": gst_data['ValDtls']['CesVal'],
            "invCessSpecificAmt": gst_data['ValDtls']['CesVal'],
            "invStateCessAmt": gst_data['ValDtls']['StCesVal'],
            "invStateCessSpecificAmt": gst_data['ValDtls']['StCesVal'],
            # "totalInvValueInWords": " FOUR THOUSAND SEVEN HUNDRED SEVENTY NINE Rupees",
            # "tranType": "O",
            "subsupplyType": gst_data['TranDtls']['SupTyp'],
            # "transporterID": "07AAECG1615N1ZK",
            # "transporterName": "Blue Dart Express Ltd",RndOffAmt
            # "transportMode": "ROAD",
            # "transportDocNo": "128765866",
            # "transportDocDate": "2021-08-12",
            # "distance": 0.00,
            # "vehicleNo": "MH01DW8378",
            # "vehicleType": "R",
            # "exchangeRt": "1.00000",
            # "companyCode": "8304",
            # "salesOrg": "8304",
            'division':company.division,
            "srcIdentifier":company.source_identifier,
            "lineItems": []
        }]
        
        line_items = []
        for item in gst_data['ItemList']:
            line_items.append({
                    "itemNo": item['SlNo'],
                    # "glCodeTaxableVal": "0060011201",
                    # "supplyType": "TAX",
                    "supplyType":gst_data['TranDtls']['SupTyp'],
                    "hsnsacCode": item['HsnCd'],
                    "itemDesc": item['PrdDesc'],
                    "itemUqc": item["Unit"],
                    "itemQty": item["Qty"],
                    "taxableVal": item["AssAmt"],
                    "igstRt": item["GstRt"] if item["IgstAmt"] > 0 else 0,
                    "igstAmt": item["IgstAmt"],
                    "cgstRt": item["GstRt"]/2 if item["GstRt"] > 0 else 0,
                    "cgstAmt": item["CgstAmt"],
                    "sgstRt": item["GstRt"]/2 if item["GstRt"] > 0 else 0,
                    "sgstAmt": item["SgstAmt"],
                    # "cessRtAdvalorem": item["CesNonAdvlAmt"],
                    # "cessAmtAdvalorem": item["CesNonAdvlAmt"],
                    "cessRtSpecific": item["CesRt"],
                    "cessAmtSpecific": item["CesAmt"],
                    "stateCessRt": item["StateCesRt"],
                    "stateCessAmt": item["StateCesAmt"],
                    # "stateCessSpecificRt": item["TotAmt"],
                    # "stateCessSpecificAmt": item["TotAmt"],
                    # "serialNoII": item["Qty"],
                    # "productName": item["Qty"],
                    "isService": item["IsServc"],
                    "unitPrice": item["Qty"],
                    "itemAmt": item["TotAmt"],
                    "totalItemAmt": item["TotItemVal"],
                    # 'lineItemAmt': item["AssAmt"]
                    "lineItemAmt":gst_data['ValDtls']['TotInvValFc']+gst_data['ValDtls']['OthChrg']
                    # "udf1": "0016090023",
                    # "udf2": "ZF1",
                    # "udf3": "Invoice (ZF1)",
                    # "udf4": "0016090023"
            })
        req[0]['lineItems'] = line_items
        # print(req,"LLLLLLLLLLLLL>>>>>>>>>>>>>>>>>>>.")
        # print(req)
        # return True
        gsp = frappe.db.get_value('GSP APIS', {"company": company.name,
                "provider":company.provider}, [
                'auth_test', 'auth_prod', 'gsp_test_app_id', 'gsp_prod_app_id',
                'gsp_prod_app_secret', 'gsp_test_app_secret', 'name',
                'gst__test_username','gst_test_password','gst__prod_username','gst_prod_password',
                'gsp_test_token','gsp_prod_token'
        ],as_dict=1)
        if company.mode == 'Testing':
            headers = {
                "apiaccesskey": gsp.gsp_test_app_id,
                "accessToken": gsp.gsp_test_token,
                "Content-Type": 'application/json',
            }
            # print('___________________________________________________')
            # print(headers)
            # print('******************************************************')
            # print(req)
            # print('___________________________________________________')
            # print(headers)
            # print(req)
            if company.proxy == 0:
                if company.skip_ssl_verify == 0:
                    irn_response = requests.post(test_irn,
                        headers=headers,
                        json={"req":req},verify=False)
                else:
                    irn_response = requests.post(test_irn,
                                                headers=headers,
                                                json={"req":req},verify=False)
            else:
                proxyhost = company.proxy_url
                proxyhost = proxyhost.replace("http://", "@")
                proxies = {
                        'https':
                        'https://' + company.proxy_username + ":" +
                        company.proxy_password + proxyhost}
                # print(proxies, "     proxy console")
                irn_response = requests.post(gsp['generate_irn'],
                                                headers=headers,
                                                json={"req":req},
                                                proxies=proxies,verify=False)

            if irn_response.status_code == 200:
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","generate_irn":'True',"status":"Success","company":company.name})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
                # return irn_response.json()
                # print()
                return format_response(invoice_number,irn_response.json(),req)
                # print(gst_data, gsp, company, invoice_number)
        else:
            headers = {
                "apiaccesskey": gsp.gsp_prod_app_id,
                "accessToken": gsp.gsp_prod_token,
                "Content-Type": 'application/json',
            }
            if company.proxy == 0:
                print(
                    prod_irn,'((((((((((((((((()))))))))))))))))',req, '***************', 
                    headers
                )
                if company.skip_ssl_verify == 0:
                    irn_response = requests.post(prod_irn,
                                                    headers=headers,
                                                    json={"req":req},verify=False)
                else:
                    irn_response = requests.post(prod_irn,
                                                headers=headers,
                                                json={"req":req},verify=False)
            else:
                proxyhost = company.proxy_url
                proxyhost = proxyhost.replace("http://", "@")
                proxies = {
                        'https':
                        'https://' + company.proxy_username + ":" +
                        company.proxy_password + proxyhost}
                # print(proxies, "     proxy console")
                irn_response = requests.post(gsp['generate_irn'],
                                                headers=headers,
                                                json={"req":req},
                                                proxies=proxies,verify=False)

            # print(irn_response.text)
            if irn_response.status_code == 200:
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","generate_irn":'True',"status":"Success","company":company.name})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
                # return irn_response.json()
                return format_response(invoice_number,irn_response.json(),req)

            # print(gst_data, gsp, company, invoice_number)
        
        
    except Exception as e:
        print(e, "post irn")
        # frappe.log_error(frappe.get_traceback(), invoice_number)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing ey_generate_einvoice ","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        # logger.error(f"{invoice_number},     postIrn,   {str(e)}")
        return {"success": False, "message": str(e)}



def format_response(invoice_number,data,request_obj):
    try:
        # print(data['errorDetails'],"**************")
        # print(data['errorDetails'] is not None)
        if data['errorDetails'] is not None:
            message = ''
            for m in data['errorDetails']:
                message = message +' '+m['errorDesc']
            response_obj = {
                "success":False,
                "message":message,
                # "ey_resp_obj":data,
                # "ey_request_obj":request_obj
            }
        else:
            response_obj = {
                "success":True,
                "result":{
                    "AckNo":data['AckNo'],
                    "AckDt":data['AckDt'],
                    "Irn":data['Irn'],
                    "SignedInvoice":data['SignedInvoice'],
                    "SignedQRCode":data['SignedQRCode'],
                    "Status":data['status'],
                    "EwbNo":data['EwbNo'],
                    "EwbDt":data['EwbDt'],
                    "EwbValidTill":data['EwbValidTill'],
                    "Remarks":data['InfoDtls'],
                },
                "ey_resp_obj":data,
                "ey_request_obj":request_obj
            }
        # print(response_obj,"**********************************8")
        return response_obj
    except Exception as e:
        print(e, "post irn")
        # frappe.log_error(frappe.get_traceback(), invoice_number)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing format_response Irn","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        # logger.error(f"{invoice_number},     postIrn,   {str(e)}")
        return {"success": False, "message": str(e)}



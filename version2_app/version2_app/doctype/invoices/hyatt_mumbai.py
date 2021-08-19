import xmltodict,frappe
import pandas as pd
import numpy as np
from version2_app.version2_app.doctype.payment_types.payment_types import *
import datetime
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice
from version2_app.version2_app.doctype.excel_upload_stats.excel_upload_stats import InsertExcelUploadStats

# @frappe.whitelist(allow_guest=True)
def hyatt_mumbai(data):
    try:
        invoice_data=data
        company =invoice_data['company']
        start_time = datetime.datetime.now()
        items=[]
        companyData = frappe.get_doc('company',company)#data['company'])
        items_data_file = invoice_data['invoice_file']
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = companyData.site_name
        items_file_path = folder_path+'/sites/'+site_folder_path+items_data_file
        with open(items_file_path) as xml_file:
            items_dataframe = xmltodict.parse(xml_file.read())
        # print(items_dataframe)
        gst_data={}
        gst_df=pd.read_excel(folder_path+'/sites/'+site_folder_path+invoice_data["gst_file"])
        # data_to_dict=gst_df
        gst_df=gst_df.iloc[0:8]
        to_dict_data=gst_df.to_dict(orient="records")
        for item in to_dict_data:
            gst_data[str(item["BILL_GENERATION_DATE"])]=item["TRX_CODE"]
        paymentTypes = GetPaymentTypes()
        paymentTypes  = [''.join(each) for each in paymentTypes['data']]
        input_data = []
        invoice_referrence_objects = {}
        invoice_number_list = [x['BILL_NO'] for x in items_dataframe["FOLIO_DETAILS"]["LIST_G_BILL_NO"]["G_BILL_NO"]]
        for each in items_dataframe["FOLIO_DETAILS"]["LIST_G_BILL_NO"]["G_BILL_NO"]:
            if each['SUMFT_DEBITPERBILL_NO']==None:
                each['SUMFT_DEBITPERBILL_NO']=0
            if each['BILL_NO'] in gst_data.keys():
                data={'invoice_category':each['FOLIO_TYPE'],'invoice_number':each['BILL_NO'],'invoice_date':each['BILL_GENERATION_DATE'],
                            'room_number':each['ROOM'],'guest_name':each['DISPLAY_NAME'],'total_invoice_amount':float(each['SUMFT_DEBITPERBILL_NO']),
                            'gstNumber':gst_data[each["BILL_NO"]],'company_code':companyData.name,'place_of_supply':companyData.state_code,'invoice_item_date_format':companyData.invoice_item_date_format,
                            'guest_data':{'invoice_category':each['FOLIO_TYPE']},'invoice_type':"B2B"}
            else:
                data={'invoice_category':each['FOLIO_TYPE'],'invoice_number':each['BILL_NO'],'invoice_date':each['BILL_GENERATION_DATE'],
                            'room_number':each['ROOM'],'guest_name':each['DISPLAY_NAME'],'total_invoice_amount':float(each['SUMFT_DEBITPERBILL_NO']),
                            'gstNumber':"",'company_code':companyData.name,'place_of_supply':companyData.state_code,'invoice_item_date_format':companyData.invoice_item_date_format,
                            'guest_data':{'invoice_category':each['FOLIO_TYPE']},'invoice_type':"B2C"}
                # data["items"]=[dict(val) for val in each["LIST_G_TRX_NO"]["G_TRX_NO"]]
            items = []
            items_pdf = []
            sac_description=frappe.db.get_list("SAC HSN CODES")
            if isinstance(each['LIST_G_TRX_NO']['G_TRX_NO'], list):
                for y,x in enumerate(each['LIST_G_TRX_NO']['G_TRX_NO']):
                    items_pdf_dict={}
                    item_date = datetime.datetime.strptime(x['TRX_DATE'],'%d-%b-%y').strftime(companyData.invoice_item_date_format)
                    # for sac_items in sac_description:
                    if x['TRANSACTION_DESCRIPTION'] in paymentTypes:# 
                        if x['FT_CREDIT'] is None:
                            x['FT_CREDIT'] = x['FT_DEBIT']
                        # if x['TRANSACTION_DESCRIPTION'] in sac_items["name"]:
                        #     items_pdf_dict = {'date':item_date,'name':x['TRANSACTION_DESCRIPTION'],"sac_code":sac_items["code"],"FT_CREDIT":float(x['FT_CREDIT'])}
                        # else:
                        items_pdf_dict = {'date':item_date,"taxcode_dsc":"No Sac","goods_desc":x["TRANSACTION_DESCRIPTION"],"taxinnum":x["TRX_NO"],'name':x['TRANSACTION_DESCRIPTION'],"sac_code":'No Sac',"FT_CREDIT":float(x['FT_CREDIT'])}
                        # continue
                    elif "CGST" in x['TRANSACTION_DESCRIPTION'] or "SGST" in x['TRANSACTION_DESCRIPTION'] or 'IGST' in x['TRANSACTION_DESCRIPTION'] or 'VAT' in x['TRANSACTION_DESCRIPTION'] or "Cess" in x['TRANSACTION_DESCRIPTION'] or "CESS" in x['TRANSACTION_DESCRIPTION']:
                        items_pdf_dict = {'date':item_date,"taxcode_dsc":"No Sac","goods_desc":x["TRANSACTION_DESCRIPTION"],"taxinnum":x["TRX_NO"],'item_value':float(x['FT_DEBIT']),'name':x['TRANSACTION_DESCRIPTION'],"sac_code":'No Sac'}
                    
                    # if x['FT_DEBIT'] is None:
                    #     x['FT_DEBIT'] = x['FT_CREDIT']
                    else:
                        if x['FT_DEBIT'] is None:
                            x['FT_DEBIT'] = x['FT_CREDIT']
                        items_dict = {'date':item_date,"goods_desc":x["TRANSACTION_DESCRIPTION"],"taxinnum":x["TRX_NO"],'item_value':float(x['FT_DEBIT']),'name':x['TRANSACTION_DESCRIPTION'],"taxcode_dsc":"No Sac",'sort_order':int(y)+1,"sac_code":'No Sac'}
                        # print(dict(x))
                        items.append(items_dict)
                        items_pdf.append(items_dict)
                    if len(items_pdf_dict)>0:
                        items_pdf.append(items_pdf_dict) 
            else:
                items_pdf_dict={}
                x = dict(each['LIST_G_TRX_NO']['G_TRX_NO'])
                item_date = datetime.datetime.strptime(x['TRX_DATE'],'%d-%b-%y').strftime(companyData.invoice_item_date_format)
                # for sac_items in sac_description:
                if x['TRANSACTION_DESCRIPTION'] in paymentTypes:# or "CGST" in x['TRANSACTION_DESCRIPTION'] or "SGST" in x['TRANSACTION_DESCRIPTION'] or 'IGST' in x['TRANSACTION_DESCRIPTION']:
                    if x['FT_CREDIT'] is None:
                        x['FT_CREDIT'] = x['FT_DEBIT']
                    
                    items_pdf_dict = {'date':item_date,'name':x['TRANSACTION_DESCRIPTION'],"sac_code":'No Sac',"FT_CREDIT":float(x['FT_CREDIT'])}
                
                elif "CGST" in x['TRANSACTION_DESCRIPTION'] or "SGST" in x['TRANSACTION_DESCRIPTION'] or 'IGST' in x['TRANSACTION_DESCRIPTION'] or 'VAT' in x['TRANSACTION_DESCRIPTION'] or 'Vat' in x['TRANSACTION_DESCRIPTION'] or "Cess" in x['TRANSACTION_DESCRIPTION'] or "CESS" in x['TRANSACTION_DESCRIPTION']:
                    
                    items_pdf_dict = {'date':item_date,'item_value':float(x['FT_DEBIT']),'name':x['TRANSACTION_DESCRIPTION'],"sac_code":'No Sac'}
                else:
                    items.append({'date':item_date,'item_value':float(x['FT_DEBIT']),'name':x['TRANSACTION_DESCRIPTION'],'sort_order':1,"sac_code":'No Sac'})
                    items_pdf.append({'date':item_date,'item_value':float(x['FT_DEBIT']),'name':x['TRANSACTION_DESCRIPTION'],"taxcode_dsc":"No Sac",'sort_order':1,"sac_code":'No Sac'})


            data['items'] = items
            refobj = data.copy()
            del refobj['items']
            refobj['items'] = items_pdf
            invoice_referrence_objects[each['BILL_NO']] = refobj
            input_data.append(data)
        output_date=[]
        taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
        frappe.publish_realtime("custom_socket", {'message':'Bulk Upload Invoices Count','type':"Bulk_upload_invoice_count","count":len(invoice_number_list),"company":company})
        countIn = 1
        for each_item in input_data:
            if each_item['invoice_category'] == "CREDIT TAX INVOICE":
                each_item['invoice_category'] = "Credit Invoice"
            elif each_item['invoice_category'] == "CREDIT INVOICE":
                each_item['invoice_category'] = "Credit Invoice"
            elif each_item['invoice_category'] == "TAX INVOICE":
                each_item['invoice_category'] = "Tax Invoice"
            else:
                each_item['invoice_category'] = "Tax Invoice"
            check_invoice = check_invoice_exists(str(each_item['invoice_number']))
            # if each['gstNumber'] == "empty":
            #     each['invoice_type'] = "B2C"
            #     each['gstNumber']=""
            # else:
            #     each['invoice_type'] = "B2B"
            if check_invoice['success']==True:
                inv_data = check_invoice['data']
                if inv_data.docstatus!=2 and inv_data.irn_generated!="Success" and inv_data.invoice_type=="B2B":
                    reupload = True
                elif inv_data.invoice_type == "B2C":
                    reupload = True
                else:
                    reupload = False
            else:
                reupload = False	
            if each_item['invoice_category'] == "empty":
                each_item['invoice_category'] = "Tax Invoice"
            each_item['invoice_from'] = "File"
            each_item['company_code'] = company
            
            each_item['invoice_date'] = each_item['invoice_date'].replace("/","-")
            each_item['invoice_date'] = each_item['invoice_date'].replace("00:00:00","")
            date_time_obj = (each_item['invoice_date'].split(":")[-1]).strip()
            date_time_obj = datetime.datetime.strptime(date_time_obj,'%d-%b-%y').strftime('%d-%b-%y %H:%M:%S')
            each_item['invoice_date'] = date_time_obj
            each_item['mode'] = companyData.mode
            each_item['invoice_file'] = ""
            
            each_item['confirmation_number'] = each_item['invoice_number']
            each_item['print_by'] = "System"
            each_item['start_time'] = str(datetime.datetime.utcnow())
            each_item['name'] = each_item['guest_name']
            error_data = {"invoice_type":'B2B' if each_item['gstNumber'] != '' else 'B2C',"invoice_number":each_item['invoice_number'],"company_code":company,"invoice_date":each_item['invoice_date']}
            error_data['invoice_file'] = ""
            error_data['guest_name'] = each_item['guest_name']
            error_data['gst_number'] = each_item['gstNumber']
            if each_item['invoice_type'] == "B2C":
                error_data['gst_number'] == ""
            error_data['state_code'] =  " "
            error_data['room_number'] = each_item['room_number']
            # invoice_referrence_objects[each_item['invoice_number']][0]['gstNumber'] = each_item['gstNumber']
            error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each_item['invoice_number']]}
            error_data['pincode'] = ""
            error_data['total_invoice_amount'] = each_item['total_invoice_amount']
            error_data['sez'] = 0
            error_data['invoice_from'] = "File"
            each_item['sez'] = 0
            sez = 0
            # print(len(each_item['gstNumber']),"lennn",each_item['gstNumber'],each_item['invoice_type'])
            taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
            if len(each_item['gstNumber']) < 15 and len(each_item['gstNumber'])>0:
                error_data['error_message'] = "Invalid GstNumber " + each_item['gstNumber']
                error_data['amened'] = 'No'
                
                errorcalulateItemsApiResponse = calulate_items(each_item)
                if errorcalulateItemsApiResponse['success'] == True:
                    error_data['items_data'] = errorcalulateItemsApiResponse['data']
                errorInvoice = Error_Insert_invoice(error_data)
                print("Error:  *******The given gst number is not a vaild one**********")
                B2B = "B2B"
                B2C = np.nan
                output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                # continue
            
            elif each_item['invoice_type']=="B2B":
                gspApiDataResponse = gsp_api_data({"code":company,"mode":companyData.mode,"provider":companyData.provider})
                checkTokenIsValidResponse = check_token_is_valid({"code":company,"mode":companyData.mode})
                if checkTokenIsValidResponse['success'] == True:
                    getTaxPayerDetailsResponse = get_tax_payer_details({"gstNumber":each_item['gstNumber'],"code":company,"invoice":str(each_item['invoice_number']),"apidata":gspApiDataResponse['data']})
                    if getTaxPayerDetailsResponse['success'] == True:
                        sez = 1 if getTaxPayerDetailsResponse["data"].tax_type == "SEZ" else 0
                        each_item['sez']=1 if getTaxPayerDetailsResponse["data"].tax_type == "SEZ" else 0
                        taxpayer=getTaxPayerDetailsResponse['data'].__dict__
                        calulateItemsApiResponse = calulate_items(each_item)
                        if calulateItemsApiResponse['success'] == True:
                            if reupload==False:
                                insertInvoiceApiResponse = insert_invoice({"guest_data":each_item,"company_code":company,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":each_item['total_invoice_amount'],"invoice_number":each_item['invoice_number'],"amened":'No',"taxpayer":taxpayer,"sez":sez,"invoice_object_from_file":{"data":invoice_referrence_objects[each_item['invoice_number']]}})
                                if insertInvoiceApiResponse['success']== True:
                                    
                                    B2B = "B2B"
                                    B2C = np.nan
                                        
                                    if insertInvoiceApiResponse['data'].irn_generated == "Success":
                                        output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Success":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                    elif insertInvoiceApiResponse['data'].irn_generated == "Pending":
                                        output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Pending":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                    else:
                                        output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Error":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                else:
                                    error_data['error_message'] = insertInvoiceApiResponse['message']
                                    error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each_item['invoice_number']]}
                                    errorInvoice = Error_Insert_invoice(error_data)
                                    B2B = "B2B"
                                    B2C = np.nan
                                    
                                    output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                    # print("B2C insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                            else:
                                insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":each_item,"company_code":company,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":each_item['total_invoice_amount'],"invoice_number":str(each_item['invoice_number']),"amened":'No',"taxpayer":taxpayer,"sez":sez,"invoice_object_from_file":{"data":invoice_referrence_objects[each_item['invoice_number']]}})
                                if insertInvoiceApiResponse['success']== True:
                                    
                                    B2B = "B2B"
                                    B2C = np.nan
                                            
                                    if insertInvoiceApiResponse['data'].irn_generated == "Success":
                                        output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Success":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                    elif insertInvoiceApiResponse['data'].irn_generated == "Pending":
                                        output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Pending":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                    else:
                                        output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Error":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                else:
                                    error_data['error_message'] = insertInvoiceApiResponse['message']
                                    error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each_item['invoice_number']]}
                                    errorInvoice = Error_Insert_invoice(error_data)
                                    B2B = "B2B"
                                    B2C = np.nan
                                    
                                    output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                    # print("B2B insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                        else:
                        
                            error_data['error_message'] = calulateItemsApiResponse['message']
                            error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each_item['invoice_number']]}
                            errorInvoice = Error_Insert_invoice(error_data)
                            B2B = "B2B"
                            B2C = np.nan
                            
                            output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                            # print("calulateItemsApi fialed:  ",calulateItemsApiResponse['message'])
                    else:
                        error_data['error_message'] = "Invalid GstNumber " + each_item['gstNumber']
                        error_data['amened'] = 'No'
                        
                        errorcalulateItemsApiResponse = calulate_items(each_item)
                        if errorcalulateItemsApiResponse['success'] == True:
                            error_data['items_data'] = errorcalulateItemsApiResponse['data']
                        errorInvoice = Error_Insert_invoice(error_data)
                        B2B = "B2B"
                        B2C = np.nan
                        
                        output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                        print("Error:  *******The given gst number is not a vaild one**********")
                else:
                    error_data['error_message'] = "Login gsp error"
                    error_data['amened'] = 'No'
                    
                    errorcalulateItemsApiResponse = calulate_items(each_item)
                    if errorcalulateItemsApiResponse['success'] == True:
                        error_data['items_data'] = errorcalulateItemsApiResponse['data']
                    errorInvoice = Error_Insert_invoice(error_data)
                    B2B = "B2B"
                    B2C = np.nan
                    frappe.log_error(errorInvoice, 'enques')
                    output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                    print("Error:  *******The given gst number is not a vaild one**********")		
            else:
                taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
                calulateItemsApiResponse = calulate_items(each_item)
                if calulateItemsApiResponse['success'] == True:
                    if reupload==False:
                        insertInvoiceApiResponse = insert_invoice({"guest_data":each_item,"company_code":company,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":each_item['total_invoice_amount'],"invoice_number":each_item['invoice_number'],"amened":'No',"taxpayer":taxpayer,"sez":sez,"invoice_object_from_file":{"data":invoice_referrence_objects[each_item['invoice_number']]}})
                        if insertInvoiceApiResponse['success']== True:
                            B2B=np.nan
                            B2C = "B2C"	 
                            if insertInvoiceApiResponse['data'].irn_generated == "Success":
                                output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Success":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                            elif insertInvoiceApiResponse['data'].irn_generated == "Pending":
                                output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Pending":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                            else:
                                output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Error":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                        else:
                            error_data['error_message'] = insertInvoiceApiResponse['message']
                            error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each_item['invoice_number']]}
                            errorInvoice = Error_Insert_invoice(error_data)

                            B2B=np.nan
                            B2C = "B2C"
                            output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                            # print("B2C insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                    else:
                        insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":each_item,"company_code":company,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":each_item['total_invoice_amount'],"invoice_number":str(each_item['invoice_number']),"amened":'No',"taxpayer":taxpayer,"sez":sez,"invoice_object_from_file":{"data":invoice_referrence_objects[each_item['invoice_number']]}})
                        if insertInvoiceApiResponse['success']== True:
                            B2B=np.nan
                            B2C = "B2C"	 
                            if insertInvoiceApiResponse['data'].irn_generated == "Success":
                                output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Success":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                            elif insertInvoiceApiResponse['data'].irn_generated == "Pending":
                                output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Pending":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                            else:
                                output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Error":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                        else:
                            error_data['error_message'] = insertInvoiceApiResponse['message']
                            error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each_item['invoice_number']]}
                            errorInvoice = Error_Insert_invoice(error_data)
                            
                            B2B=np.nan
                            B2C = "B2C"
                            output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                            # print("B2B insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                else:
                        
                    error_data['error_message'] = calulateItemsApiResponse['message']
                    error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each_item['invoice_number']]}
                    errorInvoice = Error_Insert_invoice(error_data)
                    B2C = "B2C"
                    B2B = np.nan
                    
                    output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                    # print("calulateItemsApi fialed:  ",calulateItemsApiResponse['message'])
            frappe.publish_realtime("custom_socket", {'message':'Bulk Invoice Created','type':"Bulk_file_invoice_created","invoice_number":str(each_item['invoice_number']),"company":company})
            countIn+=1
        df = pd.DataFrame(output_date)
        df = df.groupby('date').count().reset_index()
        output_data = df.to_dict('records')
        # data['UserName'] = "Ganesh"
        InsertExcelUploadStats({"data":output_data,"uploaded_by":invoice_data['username'],"start_time":str(start_time),"referrence_file":invoice_data['invoice_file'],"gst_file":invoice_data['gst_file']})
        frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Created','type':"Bulk_upload_data","data":output_data,"company":company})
        # return {"success":True,"message":"Successfully Uploaded Invoices","data":output_data}		
        return {"success":True,"message":"Successfully Uploaded"}
    except Exception as e:
        print(traceback.print_exc())
        # frappe.db.delete('File', {'file_url': data['invoice_file']})
        # if "gst_file" in data:
        #     frappe.db.delete('File',{'file_url': data['gst_file']})
        frappe.db.commit()
        print(str(e),"   manual_upload")
        # frappe.log_error(frappe.get_traceback(), 'enques')
        # make_error_snapshot(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing manual_upload_data Bulk upload","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk Invoices Exception","message":str(e),"company":data['company']})
        return {"success":False,"message":str(e)}    
          #["BILL_GENERATION_DATE":"TRX_CODE"].to_json())
    # data=[dict(val) for val in each["LIST_G_TRX_NO"]["G_TRX_NO"]]
        

from __future__ import unicode_literals
from frappe.model.document import Document
import calendar
import frappe
import traceback,os,sys
import datetime
from dateutil.relativedelta import relativedelta

@frappe.whitelist(allow_guest=True)
def gspmetering(data):
    try:
        date=datetime.datetime.today()
        outputdata=[]
        if data["range"]=="this week":
            start_day = (date - datetime.timedelta(days=date.weekday())).date().day
            end_day=date.day
        elif data["range"]== "last week":
            from_date = (date + datetime.timedelta(-date.weekday(), weeks=-1)).date()
            to_date = (date + datetime.timedelta(-date.weekday() - 1)).date()
            start_day = from_date.day
            end_day=to_date.day
        elif data["range"]=="this month":
            start_day=1
            end_day=date.day
        elif data["range"]=="last month":
            date=datetime.datetime.now()
            d = date - relativedelta(months=1)
            from_date = datetime.date(d.year, d.month, 1)
            today=date.today()
            to_date = datetime.date(today.year, today.month, 1) - relativedelta(days=1)
            start_day=from_date.day
            end_day=to_date.day
        elif data["range"]=="this year":
            start_day=1
            end_day=date.month
        fields_list=["tax_payer_details","cancel_irn","get_irn_details_by_doc","login","invoice_by_irn","sync_gst_details","generate_irn"]
        data_dict={"day_wise":[]}
        day_wise={}
        for each in range(start_day,end_day+1):
            if each<10:
                each = '0'+str(each)
            else:
                each = str(each)
            if data["range"]=="last month":
                start_date=str(date.year)+'-'+str(date.month-1)+'-'+str(start_day)
                end_date=str(date.year)+'-'+str(date.month-1)+'-'+str(end_day)
                indate = str(date.year)+'-'+str(date.month-1)+'-'+each
            elif data["range"]=="this year":
                start_date=1
                end_date=date.month
                year=date.year
                date=datetime.datetime.strptime(str(each),"%m")
                indate=date.strftime("%B")
            else:
                start_date=str(date.year)+'-'+str(date.month)+'-'+str(start_day)
                end_date=str(date.year)+'-'+str(date.month)+'-'+str(end_day)
                indate =str(date.year)+'-'+str(date.month)+'-'+each
            for fields in fields_list:
                if data["range"]=="this year":
                    get_data=frappe.db.sql("""select count(name) as total_{} from `tabGsp Metering` where {}="True" and year(creation)='{}' group by year(creation) """.format(fields,fields,year),as_dict=1)
                    if get_data!=[]:
                        data_dict["total_{}".format(fields)]=get_data[0]["total_{}".format(fields)]
                    else:
                        pass
                    year=datetime.datetime.today().strftime("%Y")
                    data1=frappe.db.sql("""select count(name) as {},monthname(creation) as creation from `tabGsp Metering` where month(creation)={} and year(creation)={} and {}="True" group by '{}' """.format(fields,each,year,fields,fields),as_dict=1)
                    
                else:
                    get_data=frappe.db.get_list("Gsp Metering",filters={"creation":["between",[start_date,end_date]],fields:"True"},fields=["count(name) as total_{}".format(fields)])
                    data_dict["total_{}".format(fields)]=get_data[0]["total_{}".format(fields)]
                    data1=frappe.db.get_list("Gsp Metering",filters={"creation":["between",[indate,indate]],fields:"True"},fields=["count(name) as {}".format(fields),"creation"],group_by=fields)
                if data1 != []:
                    if indate in day_wise.keys():
                        day_wise[indate].extend(data1)
                    else:
                        day_wise[indate]=data1
        for key,val in day_wise.items():
            if val != []:
                result={}
                result.update({"creation":key})
                for i in val:
                    result.update(i)
                data_dict["day_wise"].append(result)
            else:
                data_dict["day_wise"].append({})
        if len(data_dict["day_wise"])!=end_day-start_day:
            for i in range(len(data_dict["day_wise"]),(end_day-start_day)+1):
                data_dict["day_wise"].append({})
        return {"success":True,"data":data_dict}
    except Exception as e:
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing gspmetering","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"status":False,"message":str(e)}  


@frappe.whitelist(allow_guest=True)
def gspmetering_post(data):
    get_gsp=frappe.get_doc(data)
    get_gsp.insert()

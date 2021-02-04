import frappe



def invoiceCreated(doc, method=None):
    print("Invoice Created",doc.name)
    # frappe.publish_realtime("invoice_created", "message")
    frappe.publish_realtime("custom_socket", "{'message':'Invoices Created','data':'doc.name'}")


    # frappe.subscriber.on("invoice_created", function (channel, message) {  etc, etc })

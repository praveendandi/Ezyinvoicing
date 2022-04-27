// Copyright (c) 2022, caratred and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Room Tax"] = {
    // "formatter": function (value, row, columnDef, dataContext, default_formatter) {
    //     	value = default_formatter(row, value, columnDef, dataContext);
    //         if (columnDef.id == "SGST" && dataContext["SGST"] in ["SGST 6.0","SGST 9.0","CGST 6.0","CGST 9.0","CGST 18.0","SGST 18.0"]) {
    //             value = "<span style='color:black!important;font-weight:bold'>" + value + "</span>";
    //         }
    //         // return value;
    //         // const colName = data.Totals;
    //         // let color = "black";
    //         // if(colName == 'non_compliance' && column.id != 'Totals'){
    //         //     color = 'red';
    //         // }},
    // },
	"filters": [
		{
            "fieldname": "invoice_number",
            "label": __("Invoice Number"),
            "fieldtype": "Link",
			"options": "Invoices",
            "width": "80"
        },
		{
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "width": "80",
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "width": "80",
            "default": frappe.datetime.month_end()
        }

	]
};

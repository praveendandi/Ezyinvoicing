// Copyright (c) 2016, caratred and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Summary Report"] = {
	"filters": [
		{
            "fieldname": "tax_payer_details",
            "label": __("Tax Payer"),
            "fieldtype": "Data",
			// "options": "TaxPayerDetail",
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

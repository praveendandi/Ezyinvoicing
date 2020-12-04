// Copyright (c) 2020, caratred and contributors
// For license information, please see license.txt

frappe.ui.form.on('Invoices', {
	refresh: function (frm) {
		if (frm.doc.invoice_type == 'B2B') {
			// addGetIrnButton(frm)
			if (frm.doc.irn_generated == 'Pending') {
				if (frm.doc.ready_to_generate_irn == 'Yes') {
					pendingOrSucccessIndicator(frm, 'Pending')
					addGetIrnButton(frm)
					// checkSacCodeExist(frm)
				} else {
					if (frm.doc.error_message != undefined) {
						addErrTextButton(frm)
						addReinitiateButton(frm)
					}
				}


			}
			else if (frm.doc.irn_generated == 'Success') {
				frm.disable_form()
				pendingOrSucccessIndicator(frm, 'Success')
				addIrnTextButton(frm)
				let irnGeneartedDateTime = new Date(frm.doc.irn_generated_time)
				let irnGeneartedDateTimePlusOneDay = new Date(irnGeneartedDateTime.getTime() + 1440 * 60000)
				let today = new Date()
				if (today < irnGeneartedDateTimePlusOneDay) {
					cancelIrnButton(frm)
				}
			}
			else if (frm.doc.irn_generated == 'Cancelled') {
				pendingOrSucccessIndicator(frm, 'Cancelled')
				addCacelledMessage(frm)
			}
			getGstDetails(frm.doc.gst_number)
		}
		else if(frm.doc.invoice_type == 'B2C'){
			if (frm.doc.ready_to_generate_irn == 'Yes' && frm.doc.qr_generated == 'No') {
				pendingOrSucccessIndicator(frm, 'Pending')
				addGenerateQrButton(frm)
			} else {
				if (frm.doc.error_message != undefined && frm.doc.qr_generated == 'No') {
					addErrTextButton(frm)
					addQRReinitiateButton(frm)
				}
			}
		}
	},

	onload: function (frm) {
		// createIrn(frm)
	},
	before_submit: function (frm) {
		// if (frm.doc.ir)
		frappe.validated = false;
		createIrn(frm)
		// frappe.msgprint("This got submitted");
	},
	before_save: function (frm) {

		frappe.call({
			method: "updateTaxPayerDetails",
			doc: frm.doc,
			args: {
				taxPayerDetails: {
					'address_1': frm.doc.address_1,
					'address_2': frm.doc.address_2,
					'email': frm.doc.email,
					'phone_number': frm.doc.phone_number == undefined ? '' : frm.doc.phone_number,
					'legal_name': frm.doc.legal_name,
					'trade_name': frm.doc.trade_name,
					'location': frm.doc.location,
					'gst': frm.doc.gst_number
				},
			}, callback: function (r) {
				frm.reload_doc()
				// frm.save()
			}
		})
	}

});
const checkSacCodeExist = function (frm) {
	let item_names = []
	frm.doc.items.forEach((item => {
		console.log(item)
		if (item['sac_code_found'] == "No") {
			item_names.push(item.item_name)

		}
	}))
	if (item_names.length > 0) {
		frm.remove_custom_button("GET IRN")
		frm.add_custom_button(`SAC CODE NOT FOUND FOR '${item_names.toString()}'`, function () {

		}).addClass('dangerColor')
	}

}

const addGetIrnButton = function (frm) {
	frm.add_custom_button("GET IRN", function () {
		if (frm.doc.address_1 == '' || frm.doc.address_2 == '' || frm.doc.trade_name == '' || frm.doc.location == '') {
			frappe.msgprint("address,Trade name and location should not be empty")
			// DHANDARI KALAN
		} else {
			frappe.confirm('Are you sure you want proceed?', () => {


				frappe.show_progress('Loading', 70, 100, "Please Wait we Are Working On Your Request")
				frappe.call({
					method: 'generateIrn',
					doc: frm.doc,
					args: {
						'invoice_number': frm.doc.invoice_number
					},
					callback: function (r) {
						// console.log(r)
						frappe.hide_progress()
						if (r.message.success) {
							frappe.msgprint(r.message.message)
							frm.reload_doc()
						}
						else {
							frappe.msgprint(r.message.message)
						}

					}
				})
			}, () => {
				console.log("cancelled")
			})
		}
	})
}

const addGenerateQrButton = function (frm) {
	frm.add_custom_button("GET IRN", function () {

			frappe.confirm('Are you sure you want proceed?', () => {


				frappe.show_progress('Loading', 70, 100, "Please Wait we Are Working On Your Request")
				frappe.call({
					method: 'send_invoicedata_to_gcb',
					doc: frm.doc,
					args: {
						'invoice_number': frm.doc.invoice_number
					},
					callback: function (r) {
						console.log(r)
						frappe.hide_progress()
						if (r.message.success) {
							frappe.msgprint(r.message.message)
							frm.reload_doc()
						}
						else {
							frappe.msgprint(r.message.message)
						}

					}
				})
			}, () => {
				console.log("cancelled")
			})
		
	})
}



const createIrn = function (frm) {
	frappe.show_progress('Loading', 70, 100, "Please Wait we Are Working On Your Request")
	frappe.call({
		method: 'generateIrn',
		doc: frm.doc,
		args: {
			'invoice_number': frm.doc.invoice_number
		},
		callback: function (r) {
			// console.log(r)
			frappe.hide_progress()
			if (r.message.success) {
				frappe.msgprint(r.message.message)
				frm.reload_doc();
				const temp = JSON.parse(JSON.stringify(frm.doc));
				// doc.reload()
				// frm.refresh()
				// frappe.validated = true;
				frappe.call({
					"method": "frappe.client.submit",
					"docs": temp,
					"args": {
						"doctype": temp.doctype,
						"docname": temp.name,
						"method": "frappe.client.submit",
						"doc": temp,
					},
				})
			}
			else {
				frappe.msgprint(r.message.message)
			}

		}
	})
}

const cancelIrnButton = function (frm) {
	frm.add_custom_button("CANCEL IRN", function () {
		frappe.confirm('Are you sure you want proceed?', () => {
			cancelDailog.show()
		}, () => {
			console.log("cancelled")
		})

	})
}

const addIrnTextButton = function (frm) {
	frm.add_custom_button(frm.doc.irn_number, function () {
	}).addClass("custom")
}

const addErrTextButton = function (frm) {
	frm.add_custom_button(frm.doc.error_message, function () {
	}).addClass("error_message")
}

const pendingOrSucccessIndicator = function (frm, status) {
	if (status == 'Pending') {
		frm.page.set_indicator('Pending', 'orange')
	} else if (status == 'Cancelled') {
		frm.page.set_indicator('Cancelled', 'red')
	} else {
		frm.page.set_indicator('Success', 'green')
	}
}

const cancelDailog = new frappe.ui.Dialog({
	title: 'Please Enter reason',
	fields: [
		{
			label: 'Reason',
			fieldname: 'reason',
			fieldtype: 'Data'
		}
	],
	primary_action_label: 'Submit',
	primary_action(values) {
		console.log(values);
		cancelDailog.hide();
		frappe.call({
			method: 'cancelIrn',
			doc: cur_frm.doc,
			args: {
				'invoice_number': cur_frm.doc.invoice_number,
				'reason': values.reason
			},
			callback: function (r) {
				console.log(r)
				if (r.message.success) {
					frappe.msgprint(r.message.message)
					cur_frm.reload_doc()
				}
				else {
					frappe.msgprint(r.message.message)
				}

			}
		})
	}
});

const addCacelledMessage = function (frm) {
	frm.add_custom_button("IRN CANCLLED", function () {
	})
}

//get gst details
const getGstDetails = function (gst_number) {
	frappe.call({
		method: 'getTaxPayerDetails',
		doc: cur_frm.doc,
		args: {
			'gstNumber': gst_number,
		},
		callback: function (r) {
			console.log(r)
			if (r.message.success) {
				let data = r.message.data
				cur_frm.set_value('legal_name', data.legal_name)
				cur_frm.set_value('address_1', data.address_1)
				cur_frm.set_value('email', data.email ? data.email : "")
				cur_frm.set_value('trade_name', data.trade_name)
				cur_frm.set_value('address_2', data.address_2)
				cur_frm.set_value('phone_number', data.phone_number)
				cur_frm.set_value('state_code', data.state_code)
				cur_frm.set_value('location', data.location)
				cur_frm.set_value('pincode', data.pincode)
			}
		}
	})
}

//create Reinitiate Invoice
const addReinitiateButton = function (frm) {
	frm.add_custom_button("REINTIATE IRN", function () {

		frappe.call({
			method: 'version2_app.version2_app.doctype.invoices.reinitate_parser.file_parser',
			// doc: frm.doc,
			args: {

				'invoice': frm.doc.invoice_number

			},
			callback: function (r) {
				if (r.message.success) {
					frappe.msgprint(r.message.message)
					frm.reload_doc()
				}
				else {
					frappe.msgprint(r.message.message)
				}

			}
		})
	})
}

const addQRReinitiateButton = function (frm) {
	frm.add_custom_button("REINTIATE QR", function () {

		frappe.call({
			method: 'version2_app.version2_app.doctype.invoices.reinitate_parser.file_parser',
			// doc: frm.doc,
			args: {

				'invoice': frm.doc.invoice_number

			},
			callback: function (r) {
				if (r.message.success) {
					frappe.msgprint(r.message.message)
					frm.reload_doc()
				}
				else {
					frappe.msgprint(r.message.message)
				}

			}
		})
	})
}



//address1
//location
//trade name
//trade name

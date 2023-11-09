import { HttpClient } from '@angular/common/http';
import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { ApiUrls, Doctypes } from '../../api-urls';
import { stateCode } from '../../state-codes';
import * as Moment from 'moment';
@Component({
  selector: 'app-create-invoice-manual',
  templateUrl: './create-invoice-manual.component.html',
  styleUrls: ['./create-invoice-manual.component.scss']
})
export class CreateInvoiceManualComponent implements OnInit {

  apiMethod;
  companyData;
  taxPayerDetails: any = {};
  taxDetails;
  gstNumberError;
  creditInvoice: any = {};
  stateCodes;
  place_of_supply = "";
  manualType;
  userData;
  editInvoiceInfo;
  today_date = Moment(new Date()).format('YYYY-MM-DD');
  paxEnableCompanyCode = 'RHV-01'
  constructor(
    private http: HttpClient,
    private activeModal: NgbActiveModal,
    private toastr: ToastrService,
    private router: Router,
    private activatedRoute: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.stateCodes = stateCode;
    this.activatedRoute.queryParams.subscribe((res: any) => { this.manualType = res.type })
    this.userData = JSON.parse(localStorage.getItem('login'))
    this.companyData = JSON.parse(localStorage.getItem('company'));

    console.log("editInvoiceInfo ====", this.editInvoiceInfo)
    if (this.editInvoiceInfo) {
      this.creditInvoice = this.editInvoiceInfo;
      this.taxPayerDetails = this.editInvoiceInfo;
      this.taxDetails = true;
      this.gstNumberError = false;
    }else{

      // let code = this.stateCodes.find((res:any)=>{
      //   res.tin == this.companyData?.state_code
      //   return res;
      // })
      let code = this.stateCodes.find(x => x.tin === this.companyData?.state_code);
      // console.log(code, this.companyData?.state_code)
      this.place_of_supply = code.tin
      this.creditInvoice.place_of_supply = code.state
    }
  }


  changeDescription(e): void {
    const gstNumber = e

    if (e && e.length == 15) {
      this.http.get(`${ApiUrls.getClient}?doctype=${Doctypes.TaxPayerDetail}&fieldname=name&filters=${e}`).subscribe((res: any) => {
        if (res.message) {
          const dataObj = { "data": { "code": this.companyData.company_code, "gstNumber": gstNumber } }
          this.http.post(`${ApiUrls.taxPayersDetails}`, dataObj).subscribe((res: any) => {
            try {
              if (res.message.success) {
                this.taxDetails = true;
                this.taxPayerDetails = res.message.data
                this.gstNumberError = false;
              } else {
                this.toastr.error(res.message.message);
                this.gstNumberError = true;
              }
              if (res.message) {
                this.apiMethod = res.message?.update;
                if (this.apiMethod === false) {
                  this.http.post(`${ApiUrls.taxPayerDefault}`, this.taxPayerDetails).subscribe((res: any) => {
                  })
                } else {
                  this.http.put(`${ApiUrls.taxPayerDefault}/${this.taxPayerDetails.gst_number}`, this.taxPayerDetails).subscribe((res: any) => {
                  });
                }
              }
            } catch (e) { console.log(e) }
          })

        } else {
          this.gstNumberError = true;
        }
      })
    }
  }

  modelChangeFn(e) {
    this.place_of_supply = e.tin
  }

  onSubmit(form: NgForm) {
    const formData = form.value;
    if (/\//g.test(form.form.get('invoice_number').value) == true) {
      form.form.get('invoice_number').setErrors({ specialCharacter: '"/" character not allowed' });
      form.form.get('invoice_number').markAllAsTouched();
    }
    if (form.valid) {
      if (this.editInvoiceInfo) {
        form.value.sez = form.value.sez ? 1 : 0
        let obj = {...this.taxPayerDetails, ...form.value}
        console.log(obj)
        this.activeModal.close(obj)
      } else {
        let data = {
          place_of_supply: this.place_of_supply,
          guest_name: formData.guest_name,
          invoice_number: formData.invoice_number,
          membership: '',
          invoice_date: formData.invoice_date,
          total_invoice_amount: this.manualType == 'Credit' ? -formData.total_invoice_amount : formData.total_invoice_amount,
          invoice_type: 'B2B',
          amount_before_gst: 0,
          amount_after_gst: 0,
          gst_number: this.taxPayerDetails.gst_number,
          room_number: formData.room_number ? formData.room_number : formData.invoice_number,
          confirmation_number: formData.invoice_number,
          print_by: this.userData.full_name,
          invoice_category: this.manualType === 'Credit' ? 'Credit Invoice' : this.manualType === 'Tax' ? 'Tax Invoice' : 'Debit Invoice',
          company: this.companyData.company_code,
          legal_name: this.taxPayerDetails.legal_name,
          trade_name: this.taxPayerDetails.trade_name,
          address_1: this.taxPayerDetails.address_1,
          address_2: this.taxPayerDetails.address_2,
          state_code: this.taxPayerDetails.state_code,
          location: this.taxPayerDetails.location,
          pincode: this.taxPayerDetails.pincode,
          mode: this.companyData.mode,
          sez: formData.sez ? 1 : 0,
          invoice_file: ' ',
          doctype: 'Invoices',
          has_credit_items: 'Yes',
          irn_generated: 'Draft',
          invoice_from: 'Web',
          tax_invoice_referrence_number: formData.tax_invoice_referrence_number,
          tax_invoice_referrence_date : formData.tax_invoice_referrence_date,
          note: form.value.note
        };
        this.http.post(ApiUrls.creditInvoice, data).subscribe((res: any) => {
          if (res.data) {
            const invoiceNumber = res.data.invoice_number
            this.router.navigate(['/home/manual-credit-details' + `/${invoiceNumber}`], { queryParams: { type: this.manualType } });
            this.activeModal.close()
          }
        }, (error) => {
          // const data = error.error._server_messages;
          // const errorMessage = JSON.parse(JSON.parse(data)[0]).message;
          // this.toastr.error(errorMessage);
        })
      }
    } else {
      form.form.markAllAsTouched();
    }
  }
  closeModal() {
    this.activeModal.close()
  }
}

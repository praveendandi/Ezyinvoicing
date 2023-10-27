import { HttpClient } from '@angular/common/http';
import { Component, OnInit, ViewChild } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { ApiUrls, Doctypes } from '../../api-urls';

@Component({
  selector: 'app-sac-hsn',
  templateUrl: './sac-hsn.component.html',
  styleUrls: ['./sac-hsn.component.scss']
})
export class SacHsnComponent implements OnInit {
  saccodedisable: boolean = false
  sacCodetaxable: boolean = false
  sacCodeRevenue: boolean = false
  sacCodeDetails: any = {};
  viewType;
  sacid;
  company;
  editSacHsn;
  editType;
  sacHsnCodErr;
  invoiceInfo: any;
  invoice_number;
  constructor(
    private router: Router,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private modal: NgbModal,
    private activeModal: NgbActiveModal,
    private toaster: ToastrService
  ) { }

  ngOnInit(): void {
    console.log(this.sacHsnCodErr)
    this.company = JSON.parse(localStorage.getItem('company'));
    this.getSacCodes();
    this.sacCode();
    if (this.viewType) {
      this.saccodedisable = false
    }
  }

  getSacCodes() {
    if (this.editSacHsn) {
      let sacName = this.editSacHsn?.name
      //  sacName = this.editSacHsn?.name
      // let sacName = this.editSacHsn.name.replace('+','%2B')
      // const queryParams: any = { filters: [['description', 'like', `%${sacName}%`]] };
      // queryParams.fields = JSON.stringify(["name", "transactioncode", "owner", "creation", "modified", "modified_by", "idx", "description", "sgst", "cgst", "type", "status", "igst", "taxble", "code", "company", "net", "service_charge", "vat_rate", "state_cess_rate", "central_cess_rate", "accommodation_slab", "service_charge_net", "ignore", "sac_index", "exempted", "ignore_non_taxable_items", "service_charge_rate","one_sc_applies_to_all"]);
      // queryParams.filters = JSON.stringify(queryParams.filters);
      // this.http.get(`${ApiUrls.resource}/${Doctypes.sacCodes}`, { params: queryParams }).subscribe((response: any) => {
      //   if (response.data) {
      //     console.log(response.data[0])
      //     this.sacCodeDetails = response.data[0];
      //     this.sacCodeDetails.one_sc_applies_to_all = this.sacCodeDetails?.one_sc_applies_to_all === 0 ? false : true;
      //     this.sacCodeDetails.inclusive_of_service_charge = this.sacCodeDetails?.inclusive_of_service_charge === 0 ? false : true;
      //     this.sacCodeDetails.ignore = this.sacCodeDetails?.ignore === 0 ? false : true;
      //     this.viewType = 'edit'
      //   }
      // })
      // const queryParams: any = {};
      // queryParams.doctype = `${Doctypes.sacCodes}`;
      // let sacName = this.editSacHsn.name.replace(' ','+')
      // queryParams.name = this.editSacHsn.name;
      this.http.get(`${ApiUrls.sacHsn}/${sacName}`).subscribe((res: any) => {
        console.log(res);

        if (res.data) {
          this.sacCodeDetails = res.data;
          console.log(this.sacCodeDetails)
          this.sacCodeDetails.one_sc_applies_to_all = this.sacCodeDetails?.one_sc_applies_to_all === 0 ? false : true;
          this.sacCodeDetails.inclusive_of_service_charge = this.sacCodeDetails?.inclusive_of_service_charge === 0 ? false : true;
          this.sacCodeDetails.ignore = this.sacCodeDetails?.ignore === 0 ? false : true;
          this.viewType = 'edit'
          console.log(this.company.ezy_gst_module == "1")
          if (this.company.ezy_gst_module == "1") {
            if (this.sacCodeDetails.code == "996339") {
              this.sacCodeDetails.taxble = "No"
              this.sacCodeDetails.ignore_non_taxable_items = "0"
              this.sacCodeRevenue = true
              this.sacCodetaxable = true
            }
            else if (this.sacCodeDetails.code == "912345") {
              this.sacCodeDetails.taxble = "No"
              this.sacCodeDetails.ignore_non_taxable_items = "1"
              this.sacCodeRevenue = true
              this.sacCodetaxable = true
            }
            else {
              this.sacCodetaxable = false
              this.sacCodeRevenue = false
            }

          }
          if (this.company.ezy_gst_module == "0") {
            this.saccodedisable = false
          }

        }
      })


    } else {
      this.viewType = 'add';
      this.sacCodeDetails = {
        one_sc_applies_to_all: true,
        state_cess_rate: 0,
        central_cess_rate: 0,
        vat_rate: 0,
        cgst: 0,
        sgst: 0,
        igst: 0
      };

    }
    if (this.sacHsnCodErr) {
      this.sacCodeDetails.description = this.sacHsnCodErr;
    }


  }

  closeModal() {
    this.activeModal.close("close");
  }
  onSubmit(form: NgForm): void {

    console.log('====', form.value.is_service_charge_item)
    form.value['description'] = form.value.description.trimEnd();
    form.value['one_sc_applies_to_all'] = form.value.one_sc_applies_to_all == true ? 1 : 0;
    form.value['is_service_charge_item'] = form.value.is_service_charge_item == true ? 1 : 0;
    form.value['ignore'] = form.value.ignore == true ? 1 : 0;
    form.value.service_charge_rate = form.value.one_sc_applies_to_all == true ? 0 : form.value.service_charge_rate;
    form.value.inclusive_of_service_charge = form.value.inclusive_of_service_charge === true ? 1 : 0;
    if (this.viewType === 'edit' && form.valid) {
      this.http.put(`${ApiUrls.sacHsn}/${this.editSacHsn.name}`, form.value).subscribe((res: any) => {
        try {
          if (res.data) {
            this.toaster.success('Saved');
            this.activeModal.close(res.data);
          }
        } catch (e) { console.log(e) }
      })
    } else {
      form.form.markAllAsTouched();
      if (form.valid) {
        form.value['doctype'] = Doctypes.sacCodes;
        form.value['company'] = this.company.name;

        const formData = new FormData();
        formData.append('doc', JSON.stringify(form.value));
        console.log(form.value)
        formData.append('action', 'Save');
        this.http.post(`${ApiUrls.fileSave}`, formData).subscribe((res: any) => {
          try {
            if (res) {
              this.toaster.success('Saved');
              this.activeModal.close(res);
            } else {
              this.toaster.error(res._server_messages);
            }
          } catch (e) { console.log(e) }
        }, (err) => {
          form.form.setErrors({ error: err.error.message });
        })
      }
    }
  }


  SacsynctoGST() {
    let data = {
      description: this.sacCodeDetails.description,
    }
    this.http.post(ApiUrls.manual_sync_items, data).subscribe((res: any) => {
      if (res.message.success) {
        this.toaster.success(res.message.message);
        this.getSacCodes();
      } else {
        this.toaster.error(res.message.message)
      }
    })
  }


  gstChange(e) {
    console.log(e)
    this.sacCodeDetails.sgst = e;
    this.sacCodeDetails.igst = e * 2;
  }

  sacCode() {
    let login_data = JSON.parse(localStorage.getItem('login'))
    console.log(login_data)
    // if (login_data.name == 'Administrator') {
    //   this.saccodedisable = false
    // }
    // else {
    //   this.saccodedisable = true

    // }
    if (this.company.ezy_gst_module == "1") {
      console.log('ezygst enabled')

      if (login_data.name == 'Administrator') {
        this.saccodedisable = false
      }
      else {
        this.saccodedisable = true
      }
    }
    if (this.company?.ezy_gst_module == "0") {
      console.log('ezygst disabled')
      this.saccodedisable = false

    }


  }

  numberOnly(event): boolean {
    const charCode = (event.which) ? event.which : event.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
      return false;
    }
    return true;

  }
  saccodekeysup() {
    setTimeout(() => {
      console.log(this.sacCodeDetails.code)
      if (this.company.ezy_gst_module == "1") {
        if (this.sacCodeDetails.code == "996339") {
          this.sacCodeDetails.taxble = "No"
          this.sacCodeDetails.ignore_non_taxable_items = "0"
          this.sacCodeRevenue = true
          this.sacCodetaxable = true
        }
        else if (this.sacCodeDetails.code == "912345") {
          this.sacCodeDetails.taxble = "No"
          this.sacCodeDetails.ignore_non_taxable_items = "1"
          this.sacCodeRevenue = true
          this.sacCodetaxable = true
        }
        else {
          this.sacCodetaxable = false
          this.sacCodeRevenue = false
        }
      }
      else {
        this.saccodedisable = false
      }


    }, 200);

  }
  taxable_data(event) {
    if (this.company.ezy_gst_module == "1") {
      if (this.sacCodeDetails.taxble == "Yes") {
        this.sacCodeDetails.ignore_non_taxable_items = "0"
      }
      else {
        this.sacCodeDetails.ignore_non_taxable_items = "1"

      }
    }


  }

}

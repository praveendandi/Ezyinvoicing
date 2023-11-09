import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { ApiUrls } from '../../api-urls';

@Component({
  selector: 'app-temp-sac-line',
  templateUrl: './temp-sac-line.component.html',
  styleUrls: ['./temp-sac-line.component.scss']
})
export class TempSacLineComponent implements OnInit {

  editLineItem;
  companyDetails;
  sacCodeDetails;
  invoiceNumber;
  constructor(
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private activeModal: NgbActiveModal,
    private toaster: ToastrService
  ) { }

  ngOnInit(): void {
    const queryParams: any = { filters: [['sac_index', '=', `${this.editLineItem.sac_index}`]] };
    queryParams.filters = JSON.stringify(queryParams.filters);
    this.http.get(`${ApiUrls.sacHsn}`,{ params: queryParams }).subscribe((res:any)=>{
      if(res?.data){
    this.http.get(`${ApiUrls.sacHsn}/${res.data[0].name}`).subscribe((res: any) => {
      if (res.data) {
        this.sacCodeDetails = res.data;
      
        if (this.editLineItem && this.sacCodeDetails) {
          this.editLineItem['gstEdit'] = (this.editLineItem?.cgst > 0 || this.editLineItem?.igst > 0) ? true : false;
          this.editLineItem['gstValue'] = this.editLineItem?.cgst > 0 ? 'sgst&cgst' : 'igst';
          this.editLineItem['gstRate'] = this.editLineItem?.cgst > 0 ? this.editLineItem?.gst_rate : this.editLineItem?.igst;
          this.editLineItem['vatEdit'] = this.editLineItem?.vat > 0 ? true : false;
          this.editLineItem['cessEdit'] = this.editLineItem?.state_cess_rate > 0 ? true : false;
          this.editLineItem['CentralCessEdit'] = this.editLineItem?.cess > 0 ? true : false;
          this.editLineItem['service_chargeEdit'] = this.sacCodeDetails?.service_charge === 'Yes' ? true : false;
          this.editLineItem['service_charge_rate_value'] = this.sacCodeDetails?.one_sc_applies_to_all !== 1 ? this.sacCodeDetails.service_charge_rate : this.companyDetails?.service_charge_percentage;
          this.editLineItem['service_charge_tax_applies'] = this.sacCodeDetails?.service_charge_tax_applies;
          this.editLineItem['sc_sac_code_value'] = this.sacCodeDetails?.sc_sac_code;
          this.editLineItem['sc_gst_tax_rate_value'] = this.sacCodeDetails?.sc_gst_tax_rate;
          this.editLineItem['manual_edit'] = 'Yes';
          this.editLineItem['sgst_value'] = this.editLineItem?.gst_rate / 2;
          this.editLineItem['cgst_value'] = this.editLineItem?.gst_rate / 2;
          this.editLineItem['igst_value'] = this.editLineItem?.igst;
          this.editLineItem['QuantityEdit'] = this.editLineItem?.quantity > 0 ? true : false;
          this.editLineItem['net'] = this.sacCodeDetails?.net ;
          this.editLineItem['cess_value'] = this.editLineItem.cess;
          this.editLineItem['state_cess_value'] = this.editLineItem.state_cess;
          this.editLineItem['vat_value'] = this.editLineItem.vat;
          this.editLineItem['quantity_value'] = this.editLineItem.quantity;
          this.editLineItem['net_value'] = this.editLineItem.net
        }
      }
    })
  }
})
    this.companyDetails = JSON.parse(localStorage.getItem('company'));
    console.log(this.companyDetails)



  }
  gstSelection(e) {
    console.log('Value',e)
    if(this.editLineItem.gstValue == 'sgst&cgst'){
      this.editLineItem['sgst_value'] = this.editLineItem?.gstRate / 2;
      this.editLineItem['cgst_value'] = this.editLineItem?.gstRate / 2;
    }
    if(this.editLineItem.gstValue == 'igst'){
      this.editLineItem['igst_value'] = this.editLineItem?.gstRate;
    }
  }
  gstTypeSelection(e){
    console.log("Type",e)
    if(e == 'igst'){
      this.editLineItem['gstRate'] = this.editLineItem?.igst_value;
    }
    if(e == 'sgst&cgst'){
      this.editLineItem['gstRate'] = this.editLineItem?.gst_rate;
    }

  }
  closeModal() {
    this.activeModal.close();
  }
  onSubmit(form: NgForm): void {
    
    // form.value.net = form.value.net == true ? 'Yes' : 'No'
    console.log("form value ===",form.value)
    this.activeModal.close(form.value);
  }
}

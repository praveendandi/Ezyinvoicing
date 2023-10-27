import { HttpClient } from '@angular/common/http';
import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { NgForm } from '@angular/forms';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ApiUrls } from '../../api-urls';

@Component({
  selector: 'app-split-line-items',
  templateUrl: './split-line-items.component.html',
  styleUrls: ['./split-line-items.component.scss']
})
export class SplitLineItemsComponent implements OnInit {

  editLineItemData;
  companyDetails;
  sacCodeDetails;
  constructor(
    private http: HttpClient,
    private activeModal: NgbActiveModal
  ) { }

  ngOnInit(): void {
    console.log(this.editLineItemData)
    const queryParams: any = { filters: [['sac_index', '=', `${this.editLineItemData.sac_index}`]] };
    queryParams.filters = JSON.stringify(queryParams.filters);
    this.http.get(`${ApiUrls.sacHsn}`, { params: queryParams }).subscribe((res: any) => {
      if (res?.data) {
        this.http.get(`${ApiUrls.sacHsn}/${res.data[0].name}`).subscribe((res: any) => {
          if (res.data) {
            this.sacCodeDetails = res.data;
            if (this.editLineItemData && this.sacCodeDetails) {
              this.editLineItemData['gstEdit'] = (this.editLineItemData?.gst_rate > 0 || this.editLineItemData?.igst > 0) ? true : false;
              this.editLineItemData['gstValue'] = this.editLineItemData?.gst_rate > 0 ? 'sgst&cgst' : 'igst';
              this.editLineItemData['gstRate'] = this.editLineItemData?.gst_rate > 0 ? this.editLineItemData?.gst_rate : this.editLineItemData?.igst;
              this.editLineItemData['vatEdit'] = this.editLineItemData?.vat > 0 ? true : false;
              this.editLineItemData['cessEdit'] = this.editLineItemData?.state_cess_rate > 0 ? true : false;
              this.editLineItemData['CentralCessEdit'] = this.editLineItemData?.cess > 0 ? true : false;
              this.editLineItemData['service_chargeEdit'] = this.sacCodeDetails?.service_charge === 'Yes' ? true : false;
              this.editLineItemData['service_charge_rate_value'] = this.sacCodeDetails?.one_sc_applies_to_all !== 1 ? this.sacCodeDetails.service_charge_rate : this.companyDetails?.service_charge_percentage;
              this.editLineItemData['service_charge_tax_applies'] = this.sacCodeDetails?.service_charge_tax_applies;
              this.editLineItemData['sc_sac_code_value'] = this.sacCodeDetails?.sc_sac_code;
              this.editLineItemData['sc_gst_tax_rate_value'] = this.sacCodeDetails?.sc_gst_tax_rate;
              this.editLineItemData['manual_edit'] = 'Yes';
              this.editLineItemData['sgst_value'] = this.editLineItemData?.gst_rate / 2;
              this.editLineItemData['cgst_value'] = this.editLineItemData?.gst_rate / 2;
              this.editLineItemData['igst_value'] = this.editLineItemData?.igst;
              this.editLineItemData['DiscountEdit'] = this.editLineItemData?.discount_value > 0 ? true : false;
              this.editLineItemData['QuantityEdit'] = this.editLineItemData?.quantity > 0 ? true : false;
              this.editLineItemData['net'] = this.sacCodeDetails?.net;
              this.editLineItemData['cess_value'] = this.editLineItemData.cess;
              this.editLineItemData['state_cess_value'] = this.editLineItemData.state_cess;
              this.editLineItemData['vat_value'] = this.editLineItemData.vat;
              this.editLineItemData['discount_value_value'] = this.editLineItemData.discount_value;
              this.editLineItemData['quantity_value'] = this.editLineItemData.quantity;
              this.editLineItemData['net_value'] = this.editLineItemData.net;
              this.editLineItemData['splitEdit'] = false;
            }
          }
        })
      }
    })
    this.companyDetails = JSON.parse(localStorage.getItem('company'));

  }

  gstSelection(e) {
    console.log('Value', e)
    if (this.editLineItemData.gstValue == 'sgst&cgst') {
      this.editLineItemData['sgst_value'] = this.editLineItemData?.gstRate / 2;
      this.editLineItemData['cgst_value'] = this.editLineItemData?.gstRate / 2;
    }
    if (this.editLineItemData.gstValue == 'igst') {
      this.editLineItemData['igst_value'] = this.editLineItemData?.gstRate;
    }
  }
  gstTypeSelection(e) {
    console.log("Type", e)
    if (e == 'igst') {
      this.editLineItemData['gstRate'] = this.editLineItemData?.igst_value;
    }
    if (e == 'sgst&cgst') {
      this.editLineItemData['gstRate'] = this.editLineItemData?.gst_rate;
    }

  }
  closeModal() {
    this.activeModal.close();
  }
  onSubmit(form: NgForm) {
    console.log(form.value);
    this.activeModal.close(form.value);
  }
}

import { HttpClient } from '@angular/common/http';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { DateToFilter } from 'src/app/shared/date-filter';
import { LocationModalComponent } from '../../location-modal/location-modal.component';

@Component({
  selector: 'app-additinal-info',
  templateUrl: './additinal-info.component.html',
  styleUrls: ['./additinal-info.component.scss']
})
export class AdditinalInfoComponent implements OnInit,OnDestroy {

  company: any = {};
  paramsID;
  summaryData;
  summaryData2;
  editSummaryData:any = {}
  bankDetails:any = {};
  taxpayerLocationsList: any;
  selectedLocationDetails: any;
  constructor(
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private modal: NgbModal,
    private toastr: ToastrService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.company = JSON.parse(localStorage.getItem('company'));
    this.activatedRoute.params.subscribe((res: any) => this.paramsID = res?.id)
    if (this.paramsID) {
      this.getSummaryDetails()
      this.getSummariedData()
      this.getBankDetails()
    }
  }

  getBankDetails(){
    this.http.get(`${ApiUrls.resource}/${Doctypes.bankDetails}`,{
      params:{
        filters: JSON.stringify([['company','=',this.company?.name]]),
        fields: JSON.stringify(['*'])
      }
    }).subscribe((res:any)=>{
      if(res?.data.length){
        this.bankDetails = res.data[0];
      }
    })
  }

  getSummaryDetails() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.summaries}/${this.paramsID}`).subscribe((res: any) => {
      if (res) {
        this.summaryData2 = res.data;
        console.log(this.summaryData2)
        this.locationsFilter(this.summaryData2.tax_payer_details,this.summaryData2.location)
      }
    })
  }
  getSummariedData() {
    this.http.get(`${ApiUrls.getBreakup}`, {
      params: {
        summary: this.paramsID
      }
    }).subscribe((res: any) => {
      if (res?.message?.success) {
        this.summaryData = res?.message;
      }
    })
  }

  editSummary(editSummary) {
    // this.editSummaryData = {
    //   title: this.summaryData2?.summary_title,
    //   dates: [new Date(this.summaryData2?.from_date), new Date(this.summaryData2?.to_date)] as any
    // }
    this.editSummaryData['title'] = this.summaryData2?.summary_title
    this.editSummaryData['dates'] = [new Date(this.summaryData2?.from_date), new Date(this.summaryData2?.to_date)] as any
    let modal = this.modal.open(editSummary, { size: 'md', centered: true, windowClass: 'sideMenu30'})
  }
  onSubmitSummary(form: NgForm, modal) {
    form.form.markAllAsTouched();
    if (form.valid) {
      if (window.confirm("Are you sure updating the summary info? ")) {
        const filteredDates = new DateToFilter('Invoices', 'Custom', form.value.dates as any, 'invoice_date' as any).filter;
        let obj = {
          summary_title: form.value.title,
          from_date: filteredDates[3][0],
          to_date: filteredDates[3][1],
          location :form.value.location
        }
        this.http.put(`${ApiUrls.updateSummaryData}`, { data: obj, name: this.paramsID }).subscribe((res: any) => {
          if (res?.message?.success) {
            this.toastr.success("Updated");
            modal.close('success');
            location.reload();
          } else {
            this.toastr.error("Failed to change")
          }
        })
      } else {
        // this.editSummaryData = {
        //   title: this.summaryData2?.summary_title,
        //   dates: [new Date(this.summaryData2?.from_date), new Date(this.summaryData2?.to_date)] as any
        // }
        this.editSummaryData['title'] = this.summaryData2?.summary_title
        this.editSummaryData['dates'] = [new Date(this.summaryData2?.from_date), new Date(this.summaryData2?.to_date)] as any
      }
    }
  }
  updateTermsNCondtns(termsNCndts) {
    let modal = this.modal.open(termsNCndts, { centered: true, size: 'lg' })
  }
  onSubmitTerms(form: NgForm, modal) {
    this.http.put(`${ApiUrls.resource}/${Doctypes.summaries}/${this.paramsID}`,form.value).subscribe((res: any) => {
      if (res?.data) {
        this.getSummariedData()
        this.toastr.success("Updated");
        modal.close('success');
      }
    })
  }

  locationsFilter(tax_payer_details,location){
    this.editSummaryData['location'] = location
    const queryParams: any = { filters: [] };
    queryParams.fields = JSON.stringify(['*']);
    queryParams.filters.push(['taxpayer_details','=',tax_payer_details])
    queryParams.filters = JSON.stringify(queryParams.filters);
    this.http.get(ApiUrls.taxpayerlocation, { params: queryParams }).subscribe((res:any)=>{
      this.taxpayerLocationsList = res.data
      this.changeLocation(location)
    })
  }
  changeLocation(location){
    this.taxpayerLocationsList.forEach(element => {
      if (location == element.name) {
        this.selectedLocationDetails = element
        console.log(this.selectedLocationDetails)
      }
    });
  }
  addLocation(){
    let modal = this.modal.open(LocationModalComponent, { size: 'md', centered: true ,backdrop:'static'})
    modal.componentInstance.gstNumber = this.summaryData2.tax_payer_details;
    modal.componentInstance.locationType = 'create'
    modal.result.then((data) => {
      // on close
    }, (reason) => {
      console.log(reason)
      console.log("moda dismissed")
      // this.locationsFilter()
      this.locationsFilter(this.summaryData2.tax_payer_details,reason)
      // on dismiss
    });

  }
  ngOnDestroy(): void {
    this.modal.dismissAll();
  }
}

import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnDestroy, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import moment from 'moment';
import { DateTimeAdapter } from 'ng-pick-datetime';
import { ToastrService } from 'ngx-toastr';
import { debounceTime } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { DateToFilter } from 'src/app/shared/date-filter';
import { environment } from 'src/environments/environment';
import { LocationModalComponent } from '../location-modal/location-modal.component';

@Component({
  selector: 'app-create-summary',
  templateUrl: './create-summary.component.html',
  styleUrls: ['./create-summary.component.scss']
})
export class CreateSummaryComponent implements OnInit, OnDestroy {
  onConfirmationSearch: any = new EventEmitter()

  data = new Array(20);
  step1 = true;
  step2 = false;
  step3 = false;
  summaryData: any = {}
  company:any = {}
  domain = environment.apiDomain
  eventList: any = []
  taxpayerList: any = []
  enteredConfNumber: string;
  taxpayerLocations: any = []
  taxpayertrade_name: any;
  selectedLocationDetails: any;
  disabled=false
  pageType;
  minDate;
  dateErrorMsg = ''
  // minDispatchDate = moment(new Date(this.summaryData.modified)).endOf('day').toDate();
  constructor(
    private router: Router,
    private http: HttpClient,
    public modal: NgbModal,
    public dateTimeAdapter: DateTimeAdapter<any>,
    private toastr: ToastrService
  ) {
    dateTimeAdapter.setLocale('en-IN');
  }

  ngOnInit(): void {
    this.company = JSON.parse(localStorage.getItem('company'));
    this.getEventList()
    this.getTaxPayerList()
    this.onConfirmationSearch.pipe(debounceTime(500)).subscribe((res: any) => {
      console.log(res)
      this.getTaxPayerBySearch(res)
    })
  }
  getTaxPayerBySearch(res) {
    let filters
    if (parseInt(res.slice(0, 2))) {
      filters = [['gst_number', 'like', `%${res}%`]]
    } else {
      filters = [['legal_name', 'like', `%${res}%`]]
    }
    this.http.get(ApiUrls.taxPayerDefault, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify(filters)
      }
    }).subscribe((res: any) => {
      console.log(res)
      this.taxpayerList = res.data;
      // this.reservationsfilters = res.data

    })
  }

  getTaxPayerLocations(res) {
    this.http.get(ApiUrls.taxpayerlocation, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify([['taxpayer_details', 'like', `%${res}%`]])
      }
    }).subscribe((res: any) => {
      console.log(res)
      this.taxpayerLocations = res.data;
    })
  }

  // next(each) {
  //   if (each == 1) {
  //     this.step2 = true;
  //     this.step3 = false;
  //     this.step1 = false;
  //   }
  //   if (each == 2) {
  //     this.step3 = true;
  //     this.step2 = false;
  //     this.step1 = false;
  //   }
  // }
  // prev(each) {
  //   if (each == 1) {
  //     this.step2 = false;
  //     this.step3 = false;
  //     this.step1 = true;
  //   }
  //   if (each == 2) {
  //     this.step3 = false;
  //     this.step2 = true;
  //     this.step1 = false;
  //   }
  // }

  generateInvoices() {
    this.router.navigate(['./clbs/summary-details'])
  }

  createSummary(form: NgForm) {

    form.form.markAllAsTouched();
    if (form.valid) {
      const queryParams: any = { filters: [['invoice_type', 'like', 'B2B'], ['irn_generated', 'like', 'Success']] };
      queryParams.filters.push(['gst_number', 'like', `%${this.summaryData?.tax_payer_details}%`]);
      let dates = [new Date(this.summaryData.from_date), new Date(this.summaryData.to_date)] as any;
      const filter = new DateToFilter('Invoices', 'Custom', dates as any, 'invoice_date' as any).filter;
      if (filter) {
        queryParams.filters.push(filter);
      }
      queryParams.fields = JSON.stringify(['*'])
      queryParams.filters = JSON.stringify(queryParams.filters);
      this.http.get(ApiUrls.invoices, { params: queryParams }).subscribe((res: any) => {
        if (res?.data.length) {
          form.value['doctype'] = Doctypes.summaries;
          form.value['company'] = this.company?.name;
          form.value['legal_name'] = this.taxpayertrade_name;
          form.value['from_date'] = moment(form.value.from_date).format("YYYY/MM/DD");
          form.value['to_date'] = moment(form.value.to_date).format("YYYY/MM/DD")
          console.log("==== ",form.value)
          const formData = new FormData();
          formData.append('doc', JSON.stringify(form.value));
          formData.append('action', 'Save');
          this.http.post(`${ApiUrls.fileSave}`, formData).subscribe((res: any) => {
            this.router.navigate(['./clbs/summary-details/' + res?.docs[0]?.name])
          })
        } else {
          this.disabled = true
          this.toastr.error('Invoices not found')
        }
      });

      // this.router.navigate(['./clbs/summary-details'])
      // this.next('1');
    } else {
      this.disabled = true;
      console.log("Invalid form")
    }
  }

  getInvoicesfilteredData(obj) {
    if (!obj) { return }

    const queryParams: any = { filters: [['invoice_type', 'like', 'B2B'], ['irn_generated', 'like', 'Success']] };
    queryParams.filters.push(['gst_number', 'like', `%${this.summaryData?.tax_payer_details}%`]);
    let dates = [new Date(this.summaryData.from_date), new Date(this.summaryData.to_date)] as any;
    const filter = new DateToFilter('Invoices', 'Custom', dates as any, 'invoice_date' as any).filter;
    if (filter) {
      queryParams.filters.push(filter);
    }
    queryParams.fields = JSON.stringify(['*'])
    queryParams.filters = JSON.stringify(queryParams.filters);
    this.http.get(ApiUrls.invoices, { params: queryParams }).subscribe((res: any) => {
      if (res?.data) {

      }
    });

  }


  getEventList() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.events}`, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify([]),
        limit_page_length: 'None'
      }
    }).subscribe((res: any) => {
      // console.log(res)
      if (res.data) {
        this.eventList = res?.data;
      }

    })
  }
  companySearch(taxpayer) {
    console.log("=========", taxpayer)
    this.taxpayertrade_name = '';
    this.summaryData.location = null
    this.onConfirmationSearch.emit(taxpayer.value);
    this.gettaxPayerById(this.summaryData.tax_payer_details);

  }
  itemSelection(item1) {
    console.log("===", item1);
    this.summaryData.tax_payer_details = item1.name;
    this.taxpayertrade_name = item1.trade_name;
    this.inputfocus();
    this.gettaxPayerById(item1.name);
    this.summaryData.location = null
  }
  gettaxPayerById(name) {
    // form.location =''
    // this.contactDetails.location =null
    this.selectedLocationDetails = ''
    this.http.get(ApiUrls.taxpayerlocation, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify([['taxpayer_details', '=', name], ['company', '=', this.company?.name]])
      }
    }).subscribe((res: any) => {
      console.log(res)
      this.taxpayerLocations = res.data
      this.taxpayerLocations.forEach(element => {
        if (this.summaryData.location == element.name) {
          this.selectedLocationDetails = element
        }
      });
      // this.reservationsfilters = res.data
      //   if(res.data.length == 0){
      //   this.enteredConfNumber = 'invalid'
      // }else{
      //   this.enteredConfNumber = 'valid'
      // }
    })
  }
  getTaxPayerList() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.taxPayers}`, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify([]),
        limit_page_length: 'None'
      }
    }).subscribe((res: any) => {
      // console.log(res)
      if (res.data) {
        this.taxpayerList = res?.data;
      }

    })
  }

  goback() {
    this.router.navigate(['./clbs/summaries'])
  }
  inputfocus() {
    this.enteredConfNumber = 'valid'
    const element: any = document.getElementsByClassName('paragraphClass');
    element[0].style.display = "block";
    const element2: any = document.getElementsByClassName('companyInputErrorMsg');
    element2[0].style.display = "none";
  }
  inputblur() {
    const element: any = document.getElementsByClassName('paragraphClass');
    const element2: any = document.getElementsByClassName('companyInputErrorMsg');
    setTimeout(() => {
      element[0].style.display = "none";
      element2[0].style.display = "block";
    }, 200);
  }
  openLocationModel() {
    let modal = this.modal.open(LocationModalComponent, { size: 'md', centered: true, backdrop: 'static' })
    //  modal.componentInstance.newLocationform = item;
    modal.componentInstance.gstNumber = this.summaryData.tax_payer_details;
    modal.componentInstance.locationType = "create"
    modal.result.then((data) => {
      // on close
    }, (reason) => {
      // console.log("dismissed", modal.componentInstance.location)
      this.summaryData.location = modal.componentInstance?.location
      this.gettaxPayerById(this.summaryData.tax_payer_details)
      // on dismiss
    });
  }


  selectFromDate(e){
    this.minDate = new Date(e.value)
    // this.minDate = moment(new Date(e.value)).endOf('day').toDate();
  }

  selectToDate(e){
    this.dateErrorMsg = ""
    if(e.value < this.minDate ){
      this.dateErrorMsg = "toDate Should be greater than fromDate"
    }
  }
  ngOnDestroy(): void {
    this.modal.dismissAll();
  }
}

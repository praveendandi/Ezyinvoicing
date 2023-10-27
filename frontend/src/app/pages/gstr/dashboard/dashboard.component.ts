import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import moment from 'moment';
import { ToastrService } from 'ngx-toastr';
import { switchMap, takeUntil } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { DateToFilter } from 'src/app/shared/date-filter';
import { LocalStorageService } from 'src/app/shared/services/local-storage.service';
import { MonthYearService } from 'src/app/shared/services/month-year.service';

class dashboardFilter {

  search = {
    searchBy: '',
    searchCond :'Invoice No',
    confno: '',
    invoiceType: 'B2B',
    category : '',
    filterBy: 'Custom',
    filterType: 'invoice_date',
    filterDate: '',
    month: '',
    year: '',
    // property:'all'
  };
}
@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit,OnDestroy {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  companyDetails:any;
  minDate:any; maxDate:any;
  yearsList:any = [];
  monthList:any = [];
  documentsCountGstr1;
  filters = new dashboardFilter();
  onSearch = new EventEmitter();
  invoice_recon_last_updated: any;

  constructor(
    private http:HttpClient,
    private router:Router,
    private storageService : LocalStorageService,
    private yearService: MonthYearService,
    private activatedRoute: ActivatedRoute,
    private toastr : ToastrService
  ) { }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'));

    this.yearService.years.pipe(takeUntil(this.destroyEvents))
      .subscribe((data) => this.yearsList = data);

    this.yearService.months.pipe(takeUntil(this.destroyEvents))
      .subscribe((data) => this.monthList = data);

      const d = new Date();
      let month = d.getMonth()+1;
      let year =d.getFullYear();
      this.filters.search.month = month.toString();
      this.filters.search.year = year.toString();
      this.minDate = new Date(JSON.parse(this.filters.search.year), JSON.parse(this.filters.search.month)-1, 1);
      this.maxDate = new Date(JSON.parse(this.filters.search.year), JSON.parse(this.filters.search.month), 0);

      this.setDates(month,year);
      this.gstInvoice();
      this.gstInvoiceReconLastUpdatedData()
  }


  gstr1(){
  }

  gstInvoice(){


    this.activatedRoute.queryParams.pipe(switchMap((params: any) => {
      const queryParams: any = { filters: [['invoice_type', '=', 'B2B'],['irn_generated', '=', 'Success']] };
      const from = moment(this.minDate).format('YYYY-MM-DD');
      const to = moment(this.maxDate).format('YYYY-MM-DD');
      let filterDates = ['Invoices', `${'invoice_date'}`, 'Between', [from, to]];
      queryParams.filters.push(filterDates);
      queryParams.fields = JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"]);
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.invoices}`, { params: queryParams });
      return countApi;
    })).subscribe((res: any) => {
      if(res?.data[0]){
        this.documentsCountGstr1 = res?.data[0].total_count
      }
    })
    this.getReconDetails()
  }
  gstInvoiceReconLastUpdatedData(){


    this.activatedRoute.queryParams.pipe(switchMap((params: any) => {
      // let queryParams={
      //   month:this.filters.search.month,
      //   year:this.filters.search.year
      // }
      const countApi = this.http.get(`${ApiUrls.invoice_recon_last_updated}`);
      return countApi;
    })).subscribe((res: any) => {
      console.log(res)
      if(res?.message?.success){
        this.invoice_recon_last_updated = res?.message?.date
      }
      // if(res?.data[0]){
      //   this.invoice_recon_last_updated = res?.data[0].total_count
      // }
    })
    // this.getReconDetails()
  }

  gstr2(){

  }
  selectMonthYear(e:any, type:string ){
    if (type === 'month' && e) {
      this.filters.search.month = e;
      this.setDates(e,null)
      this.updateRouterParams();
    }
    if (type === 'year' && e) {
      this.filters.search.year = e;
      this.setDates(null,e)
      this.updateRouterParams();
    }
  }

  setDates(month,year){
    let objDates ={
      month:month?month:this.filters.search.month, year:year?year : this.filters.search.year
    }
    localStorage.setItem('dateFilters',JSON.stringify(objDates));
  }

  updateRouterParams(): void {
    this.minDate = new Date(JSON.parse(this.filters.search.year), JSON.parse(this.filters.search.month)-1, 1);
    this.maxDate = new Date(JSON.parse(this.filters.search.year), JSON.parse(this.filters.search.month), 0);

    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.search = JSON.stringify(temp.search);
    this.router.navigate(['gstr/dashboard'], {
      queryParams: temp
    });
  }
  invoiceReconcilation(){
    // let year= new Date(JSON.parse(this.filters.search.year), JSON.parse(this.filters.search.month)-1, 1);
    // let month = new Date(JSON.parse(this.filters.search.year), JSON.parse(this.filters.search.month), 0);
    let data ={
      month:this.filters.search.month,
      year:this.filters.search.year
    }
    this.router.navigate(['gstr/invoice-recon-list'],{queryParams:data})
  }
  ngOnDestroy(){
    this.destroyEvents.next();
    this.destroyEvents.unsubscribe();
  }
  comingSoon(){
    this.toastr.warning('Coming Soon')
  }
  getReconDetails(){
    // let from_date = moment(this.fromDate[0]).format('YYYY-MM-DD')
    // let to_date = moment(this.toDate[1]).format('YYYY-MM-DD')
    this.http.get(`${ApiUrls.resource}/${Doctypes.reconDetails}`,{
      params:{
        fields:JSON.stringify(['*']),
        // filters:JSON.stringify([])
      }
    }).subscribe((result:any)=>{

    })
  }
}

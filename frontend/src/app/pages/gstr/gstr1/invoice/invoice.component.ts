import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { debounceTime, mergeMap, switchMap, takeUntil } from 'rxjs/operators';
import { SearchByInputService } from 'src/app/resuable/search-by-input/search-by-input.service';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { DateToFilter } from 'src/app/shared/date-filter';
import { OtpComponent } from 'src/app/shared/models/otp/otp.component';
import { LocalStorageService, Storekeys } from 'src/app/shared/services/local-storage.service';
import { MonthYearService } from 'src/app/shared/services/month-year.service';
import { environment } from 'src/environments/environment';

class InvoiceFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0;
  
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
  selector: 'app-invoice',
  templateUrl: './invoice.component.html',
  styleUrls: ['./invoice.component.scss']
})
export class InvoiceComponent implements OnInit {

  domain = environment.apiDomain;
  invoicesData: any = {}
  invoiceList: any = [];
  loginDetails: any = {};
  propertyList:any = [];
  reconcileSummary:any = {};
  searchList:any = ['Invoice No','GST No'];
  minDate:any; maxDate:any;
  filters = new InvoiceFilter();
  onSearch = new EventEmitter();

  private destroyEvents: EventEmitter<boolean> = new EventEmitter();

  constructor(
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private toastr: ToastrService,
    private yearService: MonthYearService,
    private storageService: LocalStorageService,
    private inputService: SearchByInputService,
    private modal: NgbModal
  ) { }

  ngOnInit(): void {
    this.inputService.setSearchByList(this.searchList);
    this.inputService.setInputValue(null);
    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res) { 
        // console.log(res)
       this.filters.search.invoiceType = res.type;
       this.filters.search.category = res.category;
      }
    })
    
    this.loginDetails = JSON.parse(this.storageService?.getRawValue(Storekeys?.LOGIN) || '')
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.invoiceList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });
    

    // this.yearService.years.pipe(takeUntil(this.destroyEvents))
    //   .subscribe((data) => this.yearsList = data);

    // this.yearService.months.pipe(takeUntil(this.destroyEvents))
    //   .subscribe((data) => this.monthList = data);
    // const d = new Date();
    // d.setMonth(d.getMonth() - 1);
    // let month: any = d.toLocaleString('default', { month: 'long' });
    // month = d.getMonth() + 1;
    // let year: any = d.getFullYear();
    // this.filters.search.month = month;
    // this.filters.search.year = year;
    
    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res) { 
        // console.log(res)
        if (res.search) {
          const dateBy = JSON.parse(res.search);
          this.filters.search = JSON.parse(res.search);         
        }
      }
    })

    this.yearService.getSelectedYear().pipe(takeUntil(this.destroyEvents)).subscribe((res:any)=>{
      if(!res){return;}
    this.filters.search.year = res;
    this.minDate = new Date(JSON.parse(this.filters.search.year), JSON.parse(this.filters.search.month)-1, 1);
    this.maxDate = new Date(JSON.parse(this.filters.search.year), JSON.parse(this.filters.search.month), 0);
    this.updateRouterParams();
    });
    this.yearService.getSelectedMonth().pipe(takeUntil(this.destroyEvents)).subscribe((res:any)=>{
      if(!res){return;}
    this.filters.search.month = res;
    this.minDate = new Date(JSON.parse(this.filters.search.year), JSON.parse(this.filters.search.month)-1, 1);
    this.maxDate = new Date(JSON.parse(this.filters.search.year), JSON.parse(this.filters.search.month), 0);
    this.updateRouterParams();
    });

    this.inputService.getInputValue().pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
      if (!res && res != '') { return; }
      this.filters.search.searchBy = res;
      this.updateRouterParams();
    })

    this.inputService.getSearchType().pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
      if (!res && res != '') { return; }
      this.filters.search.searchCond = res;
      this.updateRouterParams();
    })

    
   
    // if(this.loginDetails?.company){
    //   this.getPropertyDetails();      
    // }
    this.getInvoicesList();
    // this.getPropertyDetails();
  }

  getInvoicesList() {

    this.activatedRoute.queryParams.pipe(switchMap((params: any) => {
      let reconcileParams:any;
      // console.log("params ==== ",params)
      const queryParams: any = { filters: [] };
      if (this.filters.search.searchBy !== "") {
        if (this.filters.search.searchCond == 'Invoice No') {
          queryParams.filters.push(['invoice_number', 'like', `%${this.filters.search.searchBy}%`]);
        }
        if (this.filters.search.searchCond == 'GST No') {
          queryParams.filters.push(['gst_number', 'like', `%${this.filters.search.searchBy}%`]);
        }
      }
      if (this.filters.search.invoiceType != 'B2C') {
        queryParams.filters.push(['invoice_type', '=', 'B2B']);
        queryParams.filters.push(['suptyp', '=', this.filters.search.invoiceType]);
      }
      if (this.filters.search.invoiceType == 'B2C') {
        queryParams.filters.push(['invoice_type', '=', this.filters.search.invoiceType]);
      }
      if (this.filters.search.category == 'Tax') {
        queryParams.filters.push(['invoice_category', 'in', ["Tax Invoice"]]);
      }
      if (this.filters.search.category == 'Crt-Dbt') {
        queryParams.filters.push(["invoice_category", "in", ["Credit Invoice", "Debit Invoice"]]);
      }
      // if(this.filters.search.property !== 'all' && this.filters.search.property.length){
      //   queryParams.filters.push(['property','in',this.filters.search.property])
      // }
      if (this.filters.search.filterDate) {
        const filter = new DateToFilter('Invoices', this.filters.search.filterBy, this.filters.search.filterDate as any, this.filters.search.filterType as any).filter;
        if (filter) {
          queryParams.filters.push(filter);
        }
      }
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.fields = JSON.stringify(['*']);
      queryParams.filters = JSON.stringify(queryParams.filters);
      queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
      queryParams.month = this.filters.search.month;
      queryParams.year = this.filters.search.year;
      // const countApi = this.http.get(`${ApiUrls.resource}${Doctypes.invoices}`, {
      //   params: {
      //     fields: JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"]),
      //     filters: queryParams.filters
      //   }
      // });
      // const resultApi = this.http.get(`${ApiUrls.resource}${Doctypes.invoices}`, { params: queryParams });
      // return forkJoin([countApi, resultApi]);
      // reconcileParams = 
      console.log()
      reconcileParams = queryParams.filters
      this.getReconcileSummary(reconcileParams)
      const respApi = this.http.get(`${ApiUrls.getInvoices}`, { params: queryParams });
      return respApi;
    })).subscribe((res: any) => {      
      if (this.filters.currentPage == 1) {
        this.invoiceList = [];
      }
      if (res?.message?.success) {
        this.invoicesData = res?.message?.summary;
        let list: any = res?.message?.data;
        this.filters.totalCount = this.invoicesData.no_of_invoices;

        list = list.map((each: any, index: any) => {
          if (each) {
            each.index = this.invoiceList.length + index + 1;
          }
          return each;
        });
        if (list) {
          if (this.filters.currentPage !== 1) {
            this.invoiceList = this.invoiceList.concat(list);
          } else {
            this.invoiceList = list;
          }
        }
      } else {
        this.toastr.error("Failed to Load")
      }
      // const [count, data] = res;
      // this.filters.totalCount = count.data[0].total_count;

      // data.data = data.data.map((each: any, index: any) => {
      //   if (each) {
      //     each.index = this.invoiceList.length + index + 1;
      //   }
      //   return each;
      // })
      // if (data.data) {
      //   if (this.filters.currentPage !== 1) {
      //     this.invoiceList = this.invoiceList.concat(data.data);
      //   } else {
      //     this.invoiceList = data.data;
      //   }
      // }
    })


  }

  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.search = JSON.stringify(temp.search);
    this.router.navigate(['gstr/gstr1/invoice'], {
      queryParams: temp
    });
  }
  onDateFilterChange() {
    this.filters.currentPage = 1;
    this.updateRouterParams();

  }
  checkPagination(items: number): void {
    this.filters.itemsPerPage = items;
    this.filters.currentPage = 1
    this.updateRouterParams()
  }

  selectMonthYear(e: any, type: string) {
    console.log(e);
    if (type === 'month' && e) {
      this.filters.search.month = e;
      this.updateRouterParams();
    }
    if (type === 'year' && e) {
      this.filters.search.year = e;
      this.updateRouterParams();
    }
    // if (type === 'property' && e) {
    //   this.filters.search.property = e;
    //   this.updateRouterParams();
    // }
    
  }

  selectSearchCond(event: any) {
    this.filters.search.searchCond = event;
    this.filters.search.searchBy = '';
    this.updateRouterParams()
  }
  getPropertyDetails(){
    this.http.get(`${ApiUrls.resource}${Doctypes.property}`,{params:{
      fields:JSON.stringify(['*'])
    }}).subscribe((res:any)=>{
      if(res?.data){
        this.propertyList = res?.data;
      }
    })
  }

  /***Reconcilation */
  reconcilation() {
    let month = this.filters.search.month;
    let modalRes: any;
    if (JSON.parse(month) <= 9) {
      month = `0${month}`;
    }

    this.http.post(ApiUrls.reconcile, {
      // company_code: this.loginDetails?.company,
      ret_period: `${month}${this.filters.search.year}`
    }).subscribe((res: any) => {
      if(!res?.message?.sucess && res?.message?.errorCode == 'RETOTPREQUEST'){
        modalRes = this.modal.open(OtpComponent, { size: 'md', centered: true })
        modalRes?.result.then((resOtp: any) => {
          if (resOtp) {            
            this.http.post(ApiUrls.reconcile, {
              ret_period: `${month}${this.filters.search.year}`,
              otp: resOtp
            }).subscribe((res: any) => {
              if (res?.message.success) {
                this.toastr.success("Success");
                this.getInvoicesList();
              } else {
                this.toastr.error("Error")
              }
            })
          }
        })
      }
      if (res.message.sucess) {
        this.toastr.success("Reconcilation");
        this.getInvoicesList();
      }
    })
  }
  /******************* */

  /***** retSave */
  returnSave() {
    let dataObj: any = {
      // company_code: this.loginDetails?.company,
      month: typeof this.filters.search.month === 'string' ? this.filters.search.month : JSON.stringify(this.filters.search.month),
      year: typeof this.filters.search.year === 'string' ? this.filters.search.year : JSON.stringify(this.filters.search.year)
    }
    let modalRes: any;
    this.http.post(ApiUrls.retSave, dataObj).subscribe((res: any) => {
      if (res.message.success) {
        modalRes = this.modal.open(OtpComponent, { size: 'md', centered: true })
        modalRes?.result.then((resOtp: any) => {
          if (resOtp) {
            dataObj['otp'] = resOtp;
            this.http.post(ApiUrls.retSave, dataObj).subscribe((res: any) => {
              if (res?.message.success === true) {
                this.toastr.success("Success")
              } else {
                this.toastr.error("Error")
              }
            })
          }
        })
      }
    })
    // const modalRes = this.modal.open(OtpComponent, { size: 'md', centered: true })

  }
  /********* */
  
  /*********Reconcile Summary */
  getReconcileSummary(params:any){ 
    
    let obj = {
      month: this.filters.search.month,
      year : this.filters.search.year,
      filters : params
    }    
    this.http.get(`${ApiUrls.reconcileSummary}`,{params:obj}).subscribe((res:any)=>{
      if(res?.message?.success){
        this.reconcileSummary = res?.message;
      }else{
        this.reconcileSummary = {}
        this.toastr.error(res?.message?.message)
      }
    })
  }
  /*********** */

  export_invoices(){
    const queryParams: any = { filters: [] };
      if (this.filters.search.searchBy !== "") {
        if (this.filters.search.searchCond == 'Invoice No') {
          queryParams.filters.push(['invoice_number', 'like', `%${this.filters.search.searchBy}%`]);
        }
        if (this.filters.search.searchCond == 'GST No') {
          queryParams.filters.push(['gst_number', 'like', `%${this.filters.search.searchBy}%`]);
        }
      }
      if (this.filters.search.invoiceType != 'B2C') {
        queryParams.filters.push(['invoice_type', '=', 'B2B']);
        queryParams.filters.push(['suptyp', '=', this.filters.search.invoiceType]);
      }
      if (this.filters.search.invoiceType == 'B2C') {
        queryParams.filters.push(['invoice_type', '=', this.filters.search.invoiceType]);
      }
      if (this.filters.search.category == 'Tax') {
        queryParams.filters.push(['invoice_category', 'in', ["Tax Invoice"]]);
      }
      if (this.filters.search.category == 'Crt-Dbt') {
        queryParams.filters.push(["invoice_category", "in", ["Credit Invoice", "Debit Invoice"]]);
      }
      // if(this.filters.search.property !== 'all' && this.filters.search.property.length){
      //   queryParams.filters.push(['property','in',this.filters.search.property])
      // }
      if (this.filters.search.filterDate) {
        const filter = new DateToFilter('Invoices', this.filters.search.filterBy, this.filters.search.filterDate as any, this.filters.search.filterType as any).filter;
        if (filter) {
          queryParams.filters.push(filter);
        }
      }
    let obj = {
      month: this.filters.search.month,
      year : this.filters.search.year,
      filters : JSON.stringify(queryParams.filters)
    }  
    this.http.get(`${ApiUrls.export_gstr1_invoices}`,{params:obj}).subscribe((res:any)=>{
      console.log(res)
      if(res?.message?.success){
        window.open(`${this.domain}${res?.message?.file_url}`);
      }
    })
  }

  ngOnDestroy() {
    this.destroyEvents.next();
    this.destroyEvents.unsubscribe();
  }
}

import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { debounceTime, switchMap, takeUntil } from 'rxjs/operators';
import { ApiUrls } from 'src/app/shared/api-urls';
import { MonthYearService } from 'src/app/shared/services/month-year.service';

class InvoiceFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0;
  category= '';
  search = {
    status:'',
    searchBy: '',
    confno: '',
    firstName: '',
    lastName: '',
    invoiceType: 'B2B',
    filterBy: 'Custom',
    filterType: 'invoice_date',
    filterDate: '',
    month:'',   
    year:''
  };
}
@Component({
  selector: 'app-reconciliation',
  templateUrl: './reconciliation.component.html',
  styleUrls: ['./reconciliation.component.scss']
})
export class ReconciliationComponent implements OnInit, OnDestroy {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  invoiceList: any = [];
  yearsList: any = [];
  monthList: any = [];
  filters = new InvoiceFilter();
  onSearch = new EventEmitter();
  searchCond = 'Invoice No';

  constructor(
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private toastr: ToastrService,
    private yearService: MonthYearService
  ) { }

  ngOnInit(): void {
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.invoiceList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });
    this.yearService.years.pipe(takeUntil(this.destroyEvents))
    .subscribe((data) => this.yearsList = data);

  this.yearService.months.pipe(takeUntil(this.destroyEvents))
    .subscribe((data) => this.monthList = data);
  const d = new Date();
  d.setMonth(d.getMonth() - 1);
  let month: any = d.toLocaleString('default', { month: 'long' });
  month = d.getMonth() + 1;
  let year: any = d.getFullYear();
  this.filters.search.month = month;
  this.filters.search.year = year;

  this.activatedRoute.queryParams.subscribe((res: any) => {
    console.log(res)
    if (res) {
      if (res.search) {
        const dateBy = JSON.parse(res.search);
        console.log(dateBy)
        this.filters.search.month = dateBy.month;
        this.filters.search.year = dateBy.year;
      }
    }
  })

  this.getInvoicesList();
  }

  getInvoicesList() {

    this.activatedRoute.queryParams.pipe(switchMap((params: any) => {

      const queryParams: any = { filters: [] };
      
      if (this.filters.search.confno) {
        queryParams.filters.push(['invoice_number', 'like', `%${this.filters.search.confno}%`]);
      } 
      if (this.filters.search.status) {
        queryParams.filters.push(['gstr_filed', 'like', `%${this.filters.search.status}%`]);
      }     
      
      queryParams.limit_page_length = 20;
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
      const respApi = this.http.get(`${ApiUrls.getInvoices}`, { params: queryParams });
      return respApi;
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.invoiceList = [];
      }
      if (res?.message?.success) {
        // this.invoicesData = res?.message?.summary;
        let list: any = res?.message?.data;
        // this.filters.totalCount = this.invoicesData.no_of_invoices;

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
    })


  }

  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.search = JSON.stringify(temp.search);
    this.router.navigate(['gstr/reconciliation'], {
      queryParams: temp
    });
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
  }
  reconcilation(){
    let month = this.filters.search.month;
    if(JSON.parse(month) <= 9 ){
      month = `0${month}`;
    }
   
    this.http.post(ApiUrls.reconcile,{
      // company_code:'HICC-01',
      ret_period: `${month}${this.filters.search.year}`
    }).subscribe((res:any)=>{
      if(res.message.sucess){
        console.log(res);
        this.getInvoicesList();
      }
    })
  }

  ngOnDestroy(){
    this.destroyEvents.next();
    this.destroyEvents.unsubscribe();
  }
}

import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { switchMap, takeUntil } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { LocalStorageService } from 'src/app/shared/services/local-storage.service';
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
    type:'ALL',
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
  selector: 'app-nill-rated',
  templateUrl: './nill-rated.component.html',
  styleUrls: ['./nill-rated.component.scss']
})
export class NillRatedComponent implements OnInit {
  filters = new InvoiceFilter();
  month: any = '';
  year: any = '';
  invoicesData:any ={};
  nill_rated_data:any = {};
  active =1
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  nillRatedItems: any[];
  constructor(
    private yearService: MonthYearService,
    private storageService: LocalStorageService,
    private http: HttpClient,
    private activatedRoute : ActivatedRoute,
    private modal: NgbModal,
    private router: Router,
    private toastr: ToastrService
  ) { }

  ngOnInit(): void {
    let queryParams = this.activatedRoute.snapshot.queryParams
    console.log(queryParams)

    this.yearService.getSelectedYear().pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
      if (!res) { return; }
      this.year = res;
      this.nillRatedItems  =[]
      // console.log(this.year)
      if (this.month != '' && this.year != '') {
        this.filters.search.month = this.month;
        this.filters.search.year = this.year;
        this.get_nill_rated_data();
        this.get_nill_rated_items_data()
      }
    })
    this.yearService.getSelectedMonth().pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
      if (!res) { return; }
      this.month = res;
      this.nillRatedItems =[]
      // console.log(this.month)
      if (this.month != '' && this.year != '') {
        this.filters.search.month = this.month;
        this.filters.search.year = this.year;
        this.get_nill_rated_data();
        this.get_nill_rated_items_data()
      }
    })
    // this.get_nill_rated_data();
  }
  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.search = JSON.stringify(temp.search);
    this.router.navigate(['gstr/gstr1/ill-rated'], {
      queryParams: temp
    });
  }
  get_nill_rated_data(){
    this.http.get(`${ApiUrls.nill_rated_supplies}`,{params:{
      month:this.month,year:this.year
    }}).subscribe((res:any)=>{
      // console.log(res)
      if(res?.message?.success){
        this.nill_rated_data = res?.message?.data;
      }
    })
  }
  get_nill_rated_items_data(){
    this.activatedRoute.queryParams.pipe(switchMap((params: any) => {

      const queryParams: any = { filters: [] };

      // if (this.filters.search.confno) {
      //   queryParams.filters.push(['invoice_number', 'like', `%${this.filters.search.confno}%`]);
      // }
      // if (this.filters.search.type) {
      //   queryParams.filters.push(['Type', '=', `${this.filters.search.type}`]);
      // }

      queryParams.limit_page_length = 20;
      // queryParams.fields = JSON.stringify(['*']);
      queryParams.limit_page_length = this.filters.itemsPerPage;
      // queryParams.filters = JSON.stringify(queryParams.filters);
      if(this.filters.search.type){
        queryParams.Type = this.filters.search.type
      }
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
      const respApi = this.http.get(`${ApiUrls.nill_rated_items}`, { params: queryParams });
      return respApi;
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.nillRatedItems = [];
      }
      if (res?.message?.success) {
        // this.invoicesData = res?.message?.summary;
        let list: any = res?.message?.data;
        this.filters.totalCount = res?.message?.count

        list = list.map((each: any, index: any) => {
          if (each) {
            each.index = this.nillRatedItems.length + index + 1;
          }
          return each;
        });
        if (list) {
          if (this.filters.currentPage !== 1) {
            this.nillRatedItems = this.nillRatedItems.concat(list);
          } else {
            this.nillRatedItems = list;
          }
        }
      } else {
        this.toastr.error("Failed to Load")
      }
    })
    this.http.get(`${ApiUrls.nill_rated_items}`,{params:{
      month:this.month,year:this.year
    }}).subscribe((res:any)=>{
      // console.log(res)
      if(res?.message?.success){
        this.nill_rated_data = res?.message?.data;
      }
    })
  }

  checkPagination(items: number): void {
    this.filters.itemsPerPage = items;
    this.filters.currentPage = 1
    this.updateRouterParams()
  }
}

import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { debounceTime, switchMap, takeUntil } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { LocalStorageService, Storekeys } from 'src/app/shared/services/local-storage.service';
import { MonthYearService } from 'src/app/shared/services/month-year.service';

class SacHsnFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0;
  category = '';
  search = {
    searchBy:'',
    invoiceType:'',
    month: '',
    year: '',
    // property:'all'
  };
}
@Component({
  selector: 'app-sac-hsn-outward',
  templateUrl: './sac-hsn-outward.component.html',
  styleUrls: ['./sac-hsn-outward.component.scss']
})
export class SacHsnOutwardComponent implements OnInit {

  sachsnList:any =[];
  // yearsList: any = [];
  // monthList: any = [];
  loginDetails:any = {};
  propertyList:any ={};
  searchCond = 'SAC/HSN'
  filters = new SacHsnFilter();
  onSearch = new EventEmitter();
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();

  constructor(
    private yearService: MonthYearService,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private storageService : LocalStorageService,
    private toastr : ToastrService,
    private router : Router
  ) { }

  ngOnInit(): void {
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.sachsnList = [];
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
    this.yearService.getSelectedYear().pipe(takeUntil(this.destroyEvents)).subscribe((res:any)=>{
      if(!res){return;}
    this.filters.search.year = res;
    this.updateRouterParams();
    })
    this.yearService.getSelectedMonth().pipe(takeUntil(this.destroyEvents)).subscribe((res:any)=>{
      if(!res){return;}
    this.filters.search.month = res;
    this.updateRouterParams();
    })

    this.loginDetails = JSON.parse(this.storageService.getRawValue(Storekeys.LOGIN)||'')
    // if(this.loginDetails?.company){
    //   this.getPropertyDetails()
    // }

    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res) {
        if (res.search) {
          const dateBy = JSON.parse(res.search);
          this.filters.search.month = dateBy.month;
          this.filters.search.year = dateBy.year;
          // this.filters.search.property = dateBy.property;
        }
      }
    })
    this.getSACHSNSummary();
  }

  // getSACHSNSummary(){
  //   let filters: any = [] 
  //   if(this.filters.search.property !== 'all'){
  //     filters.push(['property','=',`${this.filters.search.property}`])
  //   }
  //   let obj = {
  //     month: this.filters.search.month,
  //     year : this.filters.search.year,
  //     filters : JSON.stringify(filters),
  //     limit_page_length : 2000 
  //   } 
  //   this.http.get(`${ApiUrls.sacHsnSummary}`,{params:obj}).subscribe((res:any)=>{
  //     if(res.message?.success){
  //       this.sachsnList = res?.message?.data;
  //     }
  //   })
  // }

  getSACHSNSummary() {

    this.activatedRoute.queryParams.pipe(switchMap((params: any) => {

      const queryParams: any = { filters: [] };
      if (this.filters.search.searchBy !== "") {
        if (this.searchCond == 'Invoice No') {
          queryParams.filters.push(['invoice_number', 'like', `%${this.filters.search.searchBy}%`]);
        }
        if (this.searchCond == 'GST') {
          queryParams.filters.push(['gst_number', 'like', `%${this.filters.search.searchBy}%`]);
        }
        if (this.searchCond == 'SAC/HSN') {
          queryParams.filters.push(['Sac_Code', 'like', `%${this.filters.search.searchBy}%`]);
        }
        if (this.searchCond == 'Legal Name') {
          queryParams.filters.push(['legal_name', 'like', `%${this.filters.search.searchBy}%`]);
        }
        queryParams.limit_start = 0;
        queryParams.limit_page_length = this.filters.itemsPerPage;
        this.filters.currentPage = 1
      }
      // if(this.filters.search.property !== 'all' && this.filters.search.property.length){
      //   queryParams.filters.push(['property','=',`${this.filters.search.property}`])
      // }
      if(this.filters.search.invoiceType !== ''){
        queryParams.filters.push(['invoice_type','=',`${this.filters.search.invoiceType}`])
      }
     
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.fields = JSON.stringify(['*']);
      queryParams.filters = JSON.stringify(queryParams.filters);
      queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
      queryParams.month = this.filters.search.month;
      queryParams.year = this.filters.search.year;
      const respApi = this.http.get(`${ApiUrls.sacHsnSummary}`, { params: queryParams });
      return respApi;
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.sachsnList = [];
      }
      if (res?.message?.success) {
        let list: any = res?.message?.data;
        this.filters.totalCount = res?.message?.count;

        list = list.map((each: any, index: any) => {
          if (each) {
            each.index = this.sachsnList.length + index + 1;
          }
          return each;
        });
        if (list) {
          if (this.filters.currentPage !== 1) {
            this.sachsnList = this.sachsnList.concat(list);
          } else {
            this.sachsnList = list;
          }
        }
      } else {
        this.toastr.error("Failed to Load")
      }
     
    })


  }

  // getPropertyDetails(){
  //   this.http.get(`${ApiUrls.resource}${Doctypes.property}`,{params:{
  //     fields:JSON.stringify(['*'])
  //   }}).subscribe((res:any)=>{
  //     if(res?.data){
  //       this.propertyList = res?.data;
  //     }
  //   })
  // }
  selectSearchCond(event: any) {
    this.searchCond = event;
    this.filters.search.searchBy = '';
    this.updateRouterParams()
  }
  selectMonthYear(e: any, type: string) {
    if (type === 'month' && e) {
      this.filters.search.month = e;
    }
    if (type === 'year' && e) {
      this.filters.search.year = e;
    }
    // if (type === 'property' && e) {
    //   this.filters.search.property = e;
    // }
    this.getSACHSNSummary()
  }

  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.search = JSON.stringify(temp.search);
    this.router.navigate(['gstr/gstr1/sac-hsn-outward'], {
      queryParams: temp
    });
  }
  checkPagination(items: number): void {
    this.filters.itemsPerPage = items;
    this.filters.currentPage = 1
    this.updateRouterParams()
  }

  ngOnDestroy() {
    this.destroyEvents.next();
    this.destroyEvents.unsubscribe();
  }
}

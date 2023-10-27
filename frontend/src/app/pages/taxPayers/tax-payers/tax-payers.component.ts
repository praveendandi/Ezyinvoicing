import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap, switchMapTo } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { ToastrService } from 'ngx-toastr';

class TaxPayersFilter {
  search = {
    tradeName: '',
    gstNumber: '',
    legalName: ''
  };
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  sortBy= '';
  status=''
  start= 0;
  // synced_to_erp= ''
}
@Component({
  selector: 'app-tax-payers',
  templateUrl: './tax-payers.component.html',
  styleUrls: ['./tax-payers.component.scss']
})
export class TaxPayersComponent implements OnInit {

  filters = new TaxPayersFilter();
  onSearch = new EventEmitter();
  taxPayersList = [];
  searchType = '';
  searchText = '';
  sortBy = '';
  status ='All';
  loginUser:any ={};
  loginUSerRole;
  companyDetails;
  // synced_to_erp;

  constructor(
    private http: HttpClient,
    private router: Router,
    private toastr: ToastrService,
    private activatedParams: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page
    this.onSearch.pipe(debounceTime(500)).subscribe(res => {
      this.taxPayersList = [];
      this.filters.start=0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });
    this.activatedParams.queryParams.subscribe((res: any) => {
      if (res.search) {
        const dateBy = JSON.parse(res.search)
        this.filters.search.tradeName = dateBy.tradeName;
        this.filters.search.gstNumber = dateBy.gstNumber;
        this.filters.search.legalName = dateBy.legalName;
        this.filters.sortBy = res.sortBy;
        this.filters.status = res.status;
        // this.filters.synced_to_erp = res.synced_to_erp
      }
    })
    this.getAllPayers();
    this.loginUser = JSON.parse(localStorage.getItem('login'))
    this.loginUSerRole = this.loginUser.rolesFilter.some((each)=>(each == 'ezy-IT' || each =='ezy-Finance'))
  }

  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.search = JSON.stringify(temp.search);
    this.router.navigate(['home/tax-payers'], {
      queryParams: temp
    });
  }

  checkPagination():void{
    if (this.filters.totalCount < (this.filters.itemsPerPage * this.filters.currentPage)) {
      this.filters.currentPage = 1
     this.updateRouterParams()
    }else{
      this.updateRouterParams()
    }
  }

  getAllPayers(): void {
    this.activatedParams.queryParams.pipe(switchMap((params: TaxPayersFilter)=>{
      if(this.filters.search.tradeName){
        this.searchText = this.filters.search.tradeName;
        this.searchType = 'trade_name'
      }else if(this.filters.search.legalName){
        this.searchText = this.filters.search.legalName;
        this.searchType = 'legal_name';
      }else if(this.filters.search.gstNumber){
        this.searchText = this.filters.search.gstNumber;
        this.searchType = 'gst_number';
      }
      // else  if(this.filters.synced_to_erp){
      //   this.synced_to_erp = this.filters.synced_to_erp;
      // }
      else{
        this.searchText = '';
        this.searchType = ''
      }
      if(this.filters.sortBy){
        this.sortBy = this.filters.sortBy;
      }
      if(this.filters.status){
        this.status = this.filters.status;
      }
     
      const dataBody = {
        data: {
          start: this.filters.start,
          end: this.filters.itemsPerPage,
          value: this.searchText,
          key: this.searchType,
          sortKey: this.sortBy,
          type: this.searchText ? '': 'All',
          status: this.status,
          // synced_to_erp: this.synced_to_erp
        }
      }
      return this.http.post(ApiUrls.taxPayers, dataBody)
    })).subscribe((res:any)=>{
      try {
            if (res?.message) {
              if(this.filters.start != 0){
                this.taxPayersList = this.taxPayersList.concat(res.message?.data)
              }else{
                this.taxPayersList = res.message?.data;
              }
              this.filters.totalCount = res.message.count.gstCount;
            }
          } catch (e) { console.log(e) }
    })
  }


  navigate(item, type) {
    this.router.navigate(['home/tax-payers-details'], { queryParams: { id: item.gstNumber, type }, queryParamsHandling: 'merge' })
  }


  // taxSynctoGST(){
  //   let data = {
  //     sync_mode: 'Manual',
  //     doctype: Doctypes.TaxPayerDetails,
  //     now: true
  //   }
  //   this.http.post(ApiUrls.sync_data_to_erp, data).subscribe((res: any) => {
  //     if (res.message.success) {
  //       this.toastr.success(res.message.message);
  //       this.getAllPayers();
  //     } else {
  //       this.toastr.error(res.message.message)
  //     }
  //   })
  // }


}

import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';

class TaxpayerFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 25;
  search = '';
  searchCompany='';
  start = 0;
  status = ''
}
@Component({
  selector: 'app-taxpayers',
  templateUrl: './taxpayers.component.html',
  styleUrls: ['./taxpayers.component.scss']
})
export class TaxpayersComponent implements OnInit {
  onSearch=new EventEmitter()
  filters = new TaxpayerFilter()
  taxpayerList: any=[];
  companyDetails: any;
  toastr: any;

  constructor(public http : HttpClient,public router : Router,public activatedRoute : ActivatedRoute) { }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.updateRouterParams()
  });
    this.getTaxPAyers()
  }
  updateRouterParams(): void {
    this.router.navigate(['clbs/taxpayers'], {
      queryParams: this.filters
    });
  }
  checkPagination(items: number): void {
    this.filters.itemsPerPage = items;
    this.filters.currentPage = 1
    this.updateRouterParams()
  }


getTaxPAyers(){
  this.activatedRoute.queryParams.pipe(switchMap((params: TaxpayerFilter) => {
    this.filters.search = params.search || this.filters.search;
    this.filters.searchCompany = params.searchCompany || this.filters.searchCompany;
    // this.filters.taxpayer = params.taxpayer || this.filters.taxpayer;
    const queryParams: any = { filters: [] };
    queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
    queryParams.limit_page_length = this.filters.itemsPerPage;
    if (this.filters.search) {
      queryParams.filters.push(['gst_number', 'like', `%${this.filters.search}%`]);
    }
    if (this.filters.searchCompany) {
      queryParams.filters.push(['legal_name', 'like', `%${this.filters.searchCompany}%`]);
    }
    if (this.filters.status) {
      queryParams.filters.push(['status', 'like', `%${this.filters.status}%`]);
    }

    queryParams.filters = JSON.stringify(queryParams.filters);
    queryParams.fields = JSON.stringify(['*']);
    queryParams.order_by = "`tabTaxPayerDetail`.`creation` desc";
    const countApi = this.http.get(`${ApiUrls.taxpayerdetails}`, {
      params: {
        fields: JSON.stringify(["count( `tabTaxPayerDetail`.`name`) AS total_count"]),
        filters: queryParams.filters
      }
    });
    const resultApi = this.http.get(`${ApiUrls.taxpayerdetails}`, { params: queryParams });
    return forkJoin([countApi, resultApi]);
  })).subscribe((res: any) => {
    if (this.filters.currentPage == 1) {
      this.taxpayerList = [];
    }
    const [count, data] = res;
    this.filters.totalCount = count.data[0].total_count;
    data.data = data.data.map((each: any, index) => {
      if (each) {
        each.index = this.taxpayerList.length + index + 1;
      }
      return each;
    })
    if (data.data) {
      if (this.filters.currentPage !== 1) {
        this.taxpayerList = this.taxpayerList.concat(data.data)
      } else {
        this.taxpayerList = data.data;
      }

    }
  });
 }

}

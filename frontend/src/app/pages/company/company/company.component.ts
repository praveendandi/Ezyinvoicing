import { ApiUrls } from './../../../shared/api-urls';
import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { debounceTime, switchMap } from 'rxjs/operators';

class CompanyFilter {
  /**
   * Limit start of company filter
   * i.e Items per page
   */
  itemsPerPage = 10;
  currentPage = 1;
  /**
   * Limit page length of company filter
   * page length
   */
  search = '';
}
@Component({
  selector: 'app-company',
  templateUrl: './company.component.html',
  styleUrls: ['./company.component.scss']
})
export class CompanyComponent implements OnInit {
  filters = new CompanyFilter();
  onSearch = new EventEmitter();
  companyList = [];
  p = 1;
  constructor(
    private router: Router,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => this.updateRouterParams());
    this.activatedRoute.queryParams.pipe(switchMap((params: CompanyFilter) => {
      this.filters.itemsPerPage = parseInt(params.itemsPerPage as any, 0) || this.filters.itemsPerPage;
      this.filters.currentPage = parseInt(params.currentPage as any, 0) || this.filters.currentPage;
      this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      queryParams.limit_start = this.filters.itemsPerPage;
      queryParams.limit_page_length = this.filters.currentPage - 1;
      if (this.filters.search) {
        queryParams.filters.push(['name', 'like', this.filters.search]);
      }
      queryParams.fields = JSON.stringify(['name', 'company_name', 'trade_name', 'legal_name', 'creation']);
      queryParams.filters = JSON.stringify(queryParams.filters);
      return this.http.get(ApiUrls.company, { params: queryParams });
    })).subscribe((res: any) => {
      if (res.data) {
        this.companyList = res.data;
      }
    });
  }
  updateRouterParams(): void {
    this.router.navigate(['home/company'], {
      queryParams: this.filters
    });
  }
  /**
   * Navigates company component
   * @params data
   * @params type
   */
  navigate(data: any, type: string): void {
    this.router.navigate(['/home/company-details'], { queryParams: { id: data.sNo, type } });
  }
}

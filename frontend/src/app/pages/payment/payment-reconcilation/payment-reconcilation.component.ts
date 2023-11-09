import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { DateToFilter } from 'src/app/shared/date-filter';

class paymentReconFilter {
  /**
   * Limit start of company filter
   * i.e Items per page
   */
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0
  /**
   * Limit page length of company filter
   * page length
   */
  // search = '';

  config: any;
  searchFilter = {
    invoice_number: '',
    mode: '',
    reference: '',
    amount:'',
    filterBy: 'Today',
    filterDate: '',
    filterType: 'creation',
    card_details:'',
  }

}
@Component({
  selector: 'app-payment-reconcilation',
  templateUrl: './payment-reconcilation.component.html',
  styleUrls: ['./payment-reconcilation.component.scss']
})
export class PaymentReconcilationComponent implements OnInit {
  filters = new paymentReconFilter();
  onSearch = new EventEmitter();
  paymentReconList = [];
  p = 1;
  company;
  constructor(
    private router: Router,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private modal: NgbModal,
    private toaster: ToastrService
  ) { }

  ngOnInit(): void {
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.paymentReconList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });
    this.company = JSON.parse(localStorage.getItem('company'));
    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res.search) {

        const dateBy = JSON.parse(res.search);

        this.filters.searchFilter.filterBy = dateBy.filterBy;
        this.filters.searchFilter.filterType = dateBy.filterType;
        this.filters.searchFilter.invoice_number = dateBy.invoice_number;
        this.filters.searchFilter.mode = dateBy.mode;
        this.filters.searchFilter.reference = dateBy.reference;
        this.filters.searchFilter.amount = dateBy.amount;
        this.filters.searchFilter.card_details = dateBy.card_details;
        if (dateBy.filterDate) {
          this.filters.searchFilter.filterDate = [new Date(dateBy.filterDate[0]), new Date(dateBy.filterDate[1])] as any;
        }
      }
    })
    this.getpaymentData();
  }

  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.searchFilter = JSON.stringify(temp.searchFilter);
    this.router.navigate(['home/payment-reconciliation'], {
      queryParams: temp
    });
  }
  getpaymentData(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: paymentReconFilter) => {
      // this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      
      if (this.filters.searchFilter.amount) {
        queryParams.filters.push(['item_value', 'like', `%${this.filters.searchFilter.amount}%`]);
      }
      if (this.filters.searchFilter.mode) {
        queryParams.filters.push(['payment', 'like', `%${this.filters.searchFilter.mode}%`]);
      }
      if (this.filters.searchFilter.invoice_number) {
        queryParams.filters.push(['invoice_number', 'like', `%${this.filters.searchFilter.invoice_number}%`]);
      }
      if (this.filters.searchFilter.reference) {
        queryParams.filters.push(['payment_reference', 'like', `%${this.filters.searchFilter.reference}%`]);
      }
      if (this.filters.searchFilter.card_details) {
        queryParams.filters.push(['card_details', 'like', `%${this.filters.searchFilter.card_details}%`]);
      }
      if (this.filters.searchFilter.filterBy) {
       
          if (this.filters.searchFilter.filterBy === 'Custom') {
            if (this.filters.searchFilter.filterDate) {
              const filter = new DateToFilter('Invoice Payments', this.filters.searchFilter.filterBy, this.filters.searchFilter.filterDate as any, this.filters.searchFilter.filterType as any).filter;
              if (filter) {
                queryParams.filters.push(filter);
              }
            }
          } else if (this.filters.searchFilter.filterBy !== 'All') {
            const filter = new DateToFilter('Invoice Payments', this.filters.searchFilter.filterBy, null, this.filters.searchFilter.filterType).filter;
            if (filter) {
              queryParams.filters.push(filter);
            }
          
        }
      }
      queryParams.limit_start = this.filters.start
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabInvoice Payments`.`creation` desc"
      queryParams.fields = JSON.stringify(["name","owner", "creation", "modified", "modified_by", "idx","invoice_number","date","payment","item_value","payment_reference","card_details"]);
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.paymentRecon}`, {
        params: {
          fields: JSON.stringify(["count( `tabInvoice Payments`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.paymentRecon}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.paymentReconList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each:any,index)=>{
        if(each){
        each.index = this.paymentReconList.length + index+1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.start !== 0) {
          this.paymentReconList = this.paymentReconList.concat(data.data)
        } else {
          this.paymentReconList = data.data;
        }

      }
    });
  }
  onDateFilterChange() {
    this.filters.currentPage = 1;
    if (this.filters.searchFilter.filterBy == 'Custom') {
      this.filters.searchFilter.filterDate = '';
    } else {
      this.updateRouterParams();
    }
  }
}

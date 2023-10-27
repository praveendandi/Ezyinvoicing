import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls } from 'src/app/shared/api-urls';
import { PaymentTypeService } from '../payment-type.service';
class PaymentFilter {
  search = '';
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0;
}

@Component({
  selector: 'app-payment-type',
  templateUrl: './payment-type.component.html',
  styleUrls: ['./payment-type.component.scss']
})
export class PaymentTypeComponent implements OnInit {
  paymentDetails = [];
  p = 1;
  filters = new PaymentFilter();
  onSearch = new EventEmitter();
  loginUser:any ={};
  loginUSerRole;
  companyDetails;
  constructor(
    private paymentService: PaymentTypeService,
    private router: Router,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.paymentDetails=[];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()});
    this.getTotalCountData()
    this.loginUser = JSON.parse(localStorage.getItem('login'))
    this.loginUSerRole = this.loginUser.rolesFilter.some((each)=>(each == 'ezy-IT' || each =='ezy-Finance'))
  }

  updateRouterParams(): void {
    this.router.navigate(['home/payment-type'], {
      queryParams: this.filters
    });
  }
  // checkPagination():void{
  //   if (this.filters.totalCount < (this.filters.itemsPerPage * this.filters.currentPage)) {
  //     this.filters.currentPage = 1
  //    this.updateRouterParams()
  //   }else{
  //     this.updateRouterParams()
  //   }
  // }
  /**
   * Navigates payment type component
   * @params data
   * @params type
   */
  navigate(data: any, type: string): void {
    this.router.navigate(['/home/payment-type-details'], { queryParams: { id: data.name, type }, queryParamsHandling: 'merge' });
  }

  getTotalCountData(): void {
    this.http.get(`${ApiUrls.paymentTypes}`, {
      params: {
        fields: JSON.stringify(["count( `tabPayment Types`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      this.filters.totalCount = res.data[0].total_count;
      this.getPaymentData()
    })
  }
  getPaymentData(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: PaymentFilter) => {
      this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      if (this.filters.search) {
        queryParams.filters.push(['name', 'like', `%${this.filters.search}%`]);
      }
      queryParams.limit_start = this.filters.start
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabPayment Types`.`creation` desc"
      queryParams.fields = JSON.stringify(["payment_type", "status", "company", "creation", "name"]);
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(`${ApiUrls.paymentTypes}`, {
        params: {
          fields: JSON.stringify(["count( `tabPayment Types`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.paymentTypes}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.paymentDetails = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each:any,index)=>{
        if(each){
        each.index = this.paymentDetails.length + index+1;
        }
        return each;
      })
      if (data.data) {
        // this.paymentDetails = data.data;
        if (this.filters.start !== 0) {
          this.paymentDetails = this.paymentDetails.concat(data.data)
        } else {
          this.paymentDetails = data.data;
        }
      }
    });
  }

  checkPagination(): void {
    // console.log(this.paymentDetails.length)
    // if(this.filters.itemsPerPage < this.paymentDetails.length){
      this.filters.currentPage = 1
      this.updateRouterParams()
    // }else{
    //   this.updateRouterParams() 
    // }
  }
  // getPaymentTypes(): void {
  //   this.activatedRoute.queryParams.pipe(switchMap((params: PaymentFilter) => {
  //     this.filters.itemsPerPage = parseInt(params.itemsPerPage as any, 0) || this.filters.itemsPerPage;
  //     this.filters.currentPage = parseInt(params.currentPage as any, 0) || this.filters.currentPage;
  //     this.filters.totalCount = parseInt(params.totalCount as any, 0)|| this.filters.totalCount;
  //     this.filters.search = params.search || this.filters.search;
  //     const queryParams: any = { filters: [] };

  //     if (this.filters.search) {
  //       console.log("search =====")
  //       queryParams.filters.push(['name', 'like', `%${this.filters.search}%`]);
  //       queryParams.limit_start = 0;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //       this.filters.currentPage = 1
  //     }else{
  //       console.log("search else ====")
  //       queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //     }
  //     queryParams.order_by = "`tabPayment Types`.`modified` desc"
  //     queryParams.fields = JSON.stringify(["payment_type", "status", "company", "creation", "name"]);
  //     queryParams.filters = JSON.stringify(queryParams.filters);
  //     const countApi = this.http.get(`${ApiUrls.paymentTypes}`, {
  //       params: {
  //         fields: JSON.stringify(["count( `tabPayment Types`.`name`) AS total_count"]),
  //         filters: queryParams.filters
  //       }
  //     });
  //     const resultApi = this.http.get(`${ApiUrls.paymentTypes}`, { params: queryParams });
  //     return forkJoin([countApi, resultApi]);
  //   })).subscribe((res: any) => {
  //     const [count, data] = res;
  //     this.filters.totalCount = count.data[0].total_count;
  //     if (data.data) {
  //       this.paymentDetails = data.data;
  //     }
  //   });


  // }
}

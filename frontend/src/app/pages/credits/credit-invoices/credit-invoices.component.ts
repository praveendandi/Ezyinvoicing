import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import * as Moment from 'moment';
import moment from 'moment';
import { debounceTime, switchMap } from 'rxjs/operators';
import {DateToFilter} from 'src/app/shared/date-filter'
import { environment } from 'src/environments/environment';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';

class InvoicesFilter {
  /**
   * Limit start of company filter
   * i.e Items per page
   */
  itemsPerPage = 20;
  currentPage = 1;
  start= 0;
  totalCount = 0;
  has_credit_items = 'Yes';
  /**
   * Limit page length of company filter
   * page length
   */
  search = {
    name: '',
    invoice: '',
    gstNumber: '',
    confirmation: '',
    roomNo: '',
    invoiceType: '',
    irn: '',
    sortBy: 'modified',
    filterBy: 'Today',
    filterDate: '',
    orderBy: '',
    synced_to_erp:''
  };
}

@Component({
  selector: 'app-credit-invoices',
  templateUrl: './credit-invoices.component.html',
  styleUrls: ['./credit-invoices.component.scss']
})
export class CreditInvoicesComponent implements OnInit {
  filters = new InvoicesFilter();
  onSearch = new EventEmitter();
  sortingList = [];
  invoicesList = [];
  p = 1;
  apiDomain = environment.apiDomain;
  companyDetails:any ={}
  years= [];
  selectedMonth=moment(new Date()).format('MMM')
  selectedyear = 2022;

  constructor(
    private router: Router,
    private http: HttpClient,
    private modal: NgbModal,
    private toastr: ToastrService,
    private activatedRoute: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page
    this.http.get('/assets/jsons/sortlist.json').subscribe((res: any[]) => this.sortingList = res);
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.invoicesList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()});
    if (this.activatedRoute.snapshot.queryParams.value) {
      this.filters.search.gstNumber = this.activatedRoute.snapshot.queryParams.value
      this.filters.search.gstNumber = this.activatedRoute.snapshot.queryParams.value;
      this.filters.search.filterBy = 'All';
    }
    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res.search) {
        const dateBy = JSON.parse(res.search)
        this.filters.search.filterBy = dateBy.filterBy;
        this.filters.search.irn = dateBy.irn;
        this.filters.search.confirmation = dateBy.confirmation;
        this.filters.search.gstNumber = dateBy.gstNumber;
        this.filters.search.roomNo = dateBy.roomNo;
        this.filters.search.name = dateBy.name;
        this.filters.search.invoice = dateBy.invoice;
        this.filters.search.invoiceType = dateBy.invoiceType;
        this.filters.search.synced_to_erp = dateBy.synced_to_erp;
        
      }
    })
   this.getCreditsList();
   this.getYear()
  //  this.getTotalCount();
  }

  getTotalCount():void{
    this.http.get(ApiUrls.invoices, {
      params: {
        fields: JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"])
      }
    }).subscribe((res:any)=>{
      this.filters.totalCount = res.data[0].total_count;
      this.getCreditsList()
    })
  }

  getCreditsList():void{
    this.activatedRoute.queryParams.pipe(switchMap((params: InvoicesFilter) => {
     if (params.search) {
        const temp = JSON.parse(params.search as any);
        Object.keys(this.filters.search).forEach(element => {
          if (temp[element]) {
            this.filters.search[element] = temp[element];
          }
        });
      }

      const queryParams: any = { filters: [] };
      queryParams.order_by = "`tabInvoices`.`creation` desc"

      queryParams.filters.push(['has_credit_items', 'like', 'Yes']);
      queryParams.filters.push(['invoice_from', 'like', 'Pms']);
      queryParams.filters.push(['invoice_category', 'like', 'Tax Invoice']);
      if (this.filters.search.confirmation) {
        queryParams.filters.push(['confirmation_number', 'like', `%${this.filters.search.confirmation}%`]);
        queryParams.limit_start=0
      }
      if (this.filters.search.synced_to_erp) {
        queryParams.filters.push(['synced_to_erp', 'like', `%${this.filters.search.synced_to_erp}%`]);
        queryParams.limit_start=0
      }
      if (this.filters.search.invoice) {
        queryParams.filters.push(['invoice_number', 'like', `%${this.filters.search.invoice}%`]);
        queryParams.limit_start=0
      }
      if (this.filters.search.gstNumber) {
        queryParams.filters.push(['gst_number', 'like', `%${this.filters.search.gstNumber}%`]);
        queryParams.limit_start=0
      }
      if (this.filters.search.invoiceType) {
        queryParams.filters.push(['invoice_type', '=', this.filters.search.invoiceType]);
        queryParams.limit_start=0
      }
      if (this.filters.search.irn) {
        queryParams.filters.push(['irn_generated', '=', this.filters.search.irn]);
        queryParams.limit_start=0
      }
      if (this.filters.search.name) {
        queryParams.filters.push(['legal_name', 'like', `%${this.filters.search.name}%`]);
        queryParams.limit_start=0
      }
      if (this.filters.search.roomNo) {
        queryParams.filters.push(['room_number', 'like', `%${this.filters.search.roomNo}%`]);
        queryParams.limit_start=0
      }
      if (this.filters.search.sortBy) {
        queryParams.order_by = '`tabInvoices`.`' + this.filters.search.sortBy + '`desc';
        queryParams.limit_start=0
      }


      if (this.filters.search.filterBy) {
        if (this.filters.search.filterBy === 'Custom') {
          if (this.filters.search.filterDate) {
            const filter = new DateToFilter('Invoices', this.filters.search.filterBy, this.filters.search.filterDate as any).filter;
            if (filter) {
              queryParams.filters.push(filter);
            }
          }
        } else if (this.filters.search.filterBy !== 'All') {
          const filter = new DateToFilter('Invoices', this.filters.search.filterBy).filter;
          if (filter) {
            queryParams.filters.push(filter);
          }
        }
      }
      queryParams.limit_start = this.filters.start;
      queryParams.limit_page_length = this.filters.totalCount;
      queryParams.fields = JSON.stringify(['name', 'invoice_number', 'gst_number', 'legal_name', 'guest_name', 'confirmation_number', 'room_number', 'invoice_type', 'irn_generated', 'creation', 'ready_to_generate_irn', 'has_credit_items','invoice_file','synced_to_erp','synced_date']);
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(ApiUrls.invoices, {
        params: {
          fields: JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });

      const resultApi = this.http.get(ApiUrls.invoices, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.invoicesList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each:any,index)=>{
        if(each){
        each.index = this.invoicesList.length + index+1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.start !== 0) {
          this.invoicesList = this.invoicesList.concat(data.data)
        } else {
          this.invoicesList = data.data;
        }

      }
    });
  }
  // getCreditsData():void{
  //   this.activatedRoute.queryParams.pipe(switchMap((params: InvoicesFilter) => {
  //     this.filters.itemsPerPage = parseInt(params.itemsPerPage as any, 0) || this.filters.itemsPerPage;
  //     this.filters.currentPage = parseInt(params.currentPage as any, 0) || this.filters.currentPage;
  //     this.filters.totalCount = parseInt(params.totalCount as any, 0) || this.filters.totalCount;
  //     if (params.search) {
  //       const temp = JSON.parse(params.search as any);
  //       Object.keys(this.filters.search).forEach(element => {
  //         if (temp[element]) {
  //           this.filters.search[element] = temp[element];
  //         }
  //       });
  //     }
  //     console.log(params.search);

  //     const queryParams: any = { filters: [] };
  //     queryParams.order_by = "`tabInvoices`.`modified` desc"

  //     queryParams.filters.push(['has_credit_items', 'like', 'Yes']);
  //     if (this.filters.search.confirmation) {
  //       queryParams.filters.push(['confirmation_number', 'like', `%${this.filters.search.confirmation}%`]);
  //       queryParams.limit_start = 0;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //       this.filters.currentPage = 1
  //     }
  //     else if (this.filters.search.invoice) {
  //       queryParams.filters.push(['invoice_number', 'like', `%${this.filters.search.invoice}%`]);
  //       queryParams.limit_start = 0;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //       this.filters.currentPage = 1
  //     }
  //     else if (this.filters.search.gstNumber) {
  //       queryParams.filters.push(['gst_number', 'like', `%${this.filters.search.gstNumber}%`]);
  //       queryParams.limit_start = 0;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //       this.filters.currentPage = 1
  //     }
  //     else if (this.filters.search.invoiceType) {
  //       queryParams.filters.push(['invoice_type', '=', this.filters.search.invoiceType]);
  //       queryParams.limit_start = 0;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //       this.filters.currentPage = 1
  //     }
  //     else if (this.filters.search.irn) {
  //       queryParams.filters.push(['irn_generated', '=', this.filters.search.irn]);
  //       queryParams.limit_start = 0;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //       this.filters.currentPage = 1
  //     }
  //     else if (this.filters.search.name) {
  //       queryParams.filters.push(['legal_name', 'like', `%${this.filters.search.name}%`]);
  //       queryParams.limit_start = 0;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //       this.filters.currentPage = 1
  //     }
  //     else if (this.filters.search.roomNo) {
  //       queryParams.filters.push(['room_number', 'like', `%${this.filters.search.roomNo}%`]);
  //       queryParams.limit_start = 0;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //       this.filters.currentPage = 1
  //     }
  //     else if (this.filters.search.sortBy) {
  //       queryParams.order_by = '`tabInvoices`.`' + this.filters.search.sortBy + '`desc';
  //       queryParams.limit_start = 0;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //       this.filters.currentPage = 1
  //     }
  //     else {
  //       queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //     }
  //     if (this.filters.search.filterBy) {
  //       if (this.filters.search.filterBy === 'Custom') {
  //         if (this.filters.search.filterDate) {
  //           const filter = new DateToFilter('Invoices', this.filters.search.filterBy, this.filters.search.filterDate as any).filter;
  //           if (filter) {
  //             queryParams.filters.push(filter);
  //           }
  //         }
  //       } else if (this.filters.search.filterBy !== 'All') {
  //         const filter = new DateToFilter('Invoices', this.filters.search.filterBy).filter;
  //         if (filter) {
  //           queryParams.filters.push(filter);
  //         }
  //       }
  //     }
  //     queryParams.fields = JSON.stringify(['name', 'invoice_number', 'gst_number', 'legal_name', 'guest_name', 'confirmation_number', 'room_number', 'invoice_type', 'irn_generated', 'creation', 'ready_to_generate_irn', 'has_credit_items']);
  //     queryParams.filters = JSON.stringify(queryParams.filters);
  //     const countApi = this.http.get(ApiUrls.invoices, {
  //       params: {
  //         fields: JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"]),
  //         filters: queryParams.filters
  //       }
  //     });
  //     const resultApi = this.http.get(ApiUrls.invoices, { params: queryParams });
  //     return forkJoin([countApi, resultApi]);
  //   })).subscribe((res: any) => {
  //     const [count, data] = res;
  //     this.filters.totalCount = count.data[0].total_count;
  //     if (data.data) {
  //       this.invoicesList = data.data;
  //     }
  //   });
  // }
  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.search = JSON.stringify(temp.search);
    this.router.navigate(['home/credit-invoices'], {
      queryParams: temp
    });
  }

  // checkPagination(): void {
  //   if (this.filters.totalCount < (this.filters.itemsPerPage * this.filters.currentPage)) {
  //     this.filters.currentPage = 1
  //     this.updateRouterParams()
  //   }else{
  //     this.updateRouterParams()
  //   }
  // }
  onDateFilterChange() {
    if (this.filters.search.filterBy == 'Custom') {
      this.filters.search.filterDate = '';
    } else {
      this.updateRouterParams();
    }
  }
  sortBy(type, sort): void {
    this.filters.search.sortBy = `${type}`;
    this.filters.search.orderBy = `${sort}`
    this.updateRouterParams();
  }


  print(invoice) {
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = this.apiDomain + invoice?.invoice_file;
    document.body.appendChild(iframe);
    if (iframe.src) {
      setTimeout(() => { iframe.contentWindow.print() },1000)
    }
  }

  checkPagination(): void {
    console.log(this.invoicesList.length)
    if(this.filters.itemsPerPage < this.invoicesList.length){
      this.filters.currentPage = 1
      this.updateRouterParams()
    }else{
      this.updateRouterParams() 
    }
  }


  // synctoGST(){
  //   this.http.get(ApiUrls.bulk_sync_ezygst).subscribe((res: any) => {
  //     if (res.message.success) {
  //       this.toastr.success(res.message.message);
  //       this.getCreditsList();
  //     } else {
  //       this.toastr.error(res.message.message)
  //     }
  //   })
  // }

  // syncModel(content) {
  //   this.modal.open(content, {size:'md', centered: true,});
  // }
  

  getYear(){
    var currentYear = new Date().getFullYear()
    var startYear = currentYear;
    for(var i=startYear; i<= currentYear; i++){
      this.years.push(startYear++);
    }
    return this.years;
 }
}


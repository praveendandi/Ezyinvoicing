import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { DateToFilter } from 'src/app/shared/date-filter';

class InvoicesFilter {
  /**
   * Limit start of company filter
   * i.e Items per page
   */
  // itemsPerPage = 50;
  // currentPage = 1;
  // totalCount = 0;
  // start = 0
  /**
   * Limit page length of company filter
   * page length
   */
  search = {

    invoice: '',
    gstNumber: '',
    // sortBy: 'modified',
    // filterBy: 'Today',
    filterDate: '',
    // orderBy: '',
    // filterType: 'creation'
  };
}
@Component({
  selector: 'app-invoices',
  templateUrl: './invoices.component.html',
  styleUrls: ['./invoices.component.scss']
})
export class InvoicesComponent implements OnInit {
  filters = new InvoicesFilter();
  onSearch = new EventEmitter();
  onInvoiceSearch = new EventEmitter()

  paramsID: any
  summaryData: any = {};
  invoicesData: any = [];
  dupinvoicesList: any = []
  selectAll = false;
  data = new Array(20)
  pageType: any;
  addB2CEnable = false
  b2cInvoiceList:any = []
  b2cInvoicedetails ={
    invoice :''
  }
  constructor(
    private http: HttpClient,
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private toastr : ToastrService
  ) { }

  ngOnInit(): void {
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => this.updateRouterParams());
    this.activatedRoute.params.subscribe((res: any) => {
      console.log(res)
      this.pageType = res?.type
      this.paramsID = res?.id
    })
    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res?.search) {
        let data = JSON.parse(res?.search);
        this.filters.search = data;
      }
    })
    this.getSummaryDetails();
    this.onInvoiceSearch.pipe(debounceTime(500)).subscribe((res: any) => {
      console.log(res)
     if(res){
      this.getB2CInvoices(res);
     }

    })
  }

  getSummaryDetails() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.summaries}/${this.paramsID}`).subscribe((res: any) => {
      if (res) {
        this.summaryData = res.data;
        // let summaryData = res.data;
        this.filters.search.filterDate = [new Date(this.summaryData.from_date), new Date(this.summaryData.to_date)] as any;
        this.getInvoicesfilteredData(this.summaryData)
      }
    })
  }
  getInvoicesfilteredData(obj) {
    if (!obj) { return }
    this.activatedRoute.queryParams.pipe(switchMap((params: InvoicesFilter) => {
      const queryParams: any = { filters: [['invoice_type', 'like', 'B2B'], ['irn_generated', 'like', 'Success']] };
      queryParams.filters.push(['summary','!=',this.paramsID])
      if (this.summaryData?.tax_payer_details) {
        queryParams.filters.push(['gst_number', 'like', `%${this.summaryData?.tax_payer_details}%`]);
      }
      if (this.filters?.search?.invoice) {
        queryParams.filters.push(['invoice_number', 'like', `%${this.filters?.search?.invoice}%`]);
      }
      if (this.filters.search.filterDate) {
        const filter = new DateToFilter('Invoices', 'Custom', this.filters.search.filterDate as any, 'invoice_date' as any).filter;
        if (filter) {
          queryParams.filters.push(filter);
        }
      }

      queryParams.limit_page_length = 'None';
      queryParams.fields = JSON.stringify(['*'])
      queryParams.filters = JSON.stringify(queryParams.filters);
      queryParams.order_by = "`tabInvoices`.`creation` desc";
      const countApi = this.http.get(ApiUrls.invoices, {
        params: {
          fields: JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(ApiUrls.invoices, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res:any)=>{
      const [count, data] = res;

      this.invoicesData = data?.data.map((each: any, index) => {
        if (each) {
          each.index = this.invoicesData.length + index + 1;
          each['checked'] = false;
        }
        return each;
      })
      this.dupinvoicesList = [];
    })


    // const queryParams: any = { filters: [['invoice_type', 'like', 'B2B'], ['irn_generated', 'like', 'Success']] };
    // if (this.summaryData?.tax_payer_details) {
    //   queryParams.filters.push(['gst_number', 'like', `%${this.summaryData?.tax_payer_details}%`]);
    // }
    // if (this.summaryData.from_date) {
    //   const filter = new DateToFilter('Invoices', 'Custom', [this.summaryData.from_date, this.summaryData.to_date] as any, 'invoice_date' as any).filter;
    //   console.log(filter)
    //   if (filter) {
    //     queryParams.filters.push(filter);
    //   }
    // }
    // queryParams.limit_page_length = 'None';
    // queryParams.fields = JSON.stringify(['*'])
    // queryParams.filters = JSON.stringify(queryParams.filters);
    // this.http.get(`${ApiUrls.resource}/${Doctypes.invoices}`, { params: queryParams }).subscribe((res: any) => {
    //   if (res?.data) {

    //     this.invoicesData = res?.data.map((each: any, index) => {
    //       if (each) {
    //         each.index = this.invoicesData.length + index + 1;
    //         each['checked'] = false;
    //       }
    //       return each;
    //     })
    //     this.dupinvoicesList = [];
    //   }
    // })
  }

  checkedItemsAll(event) {
    if (this.selectAll) {
      this.dupinvoicesList = this.invoicesData.filter((each: any) => {
        each.checked = true
        return each;
      })
    } else {
      this.dupinvoicesList = this.invoicesData.filter((each: any) => {
        each.checked = false
        return each;
      })
    }
    this.dupinvoicesList = this.invoicesData.filter((each: any) => each.checked && !each.summary)
    this.dupinvoicesList = this.dupinvoicesList.map((each: any) => {
      if (each) {
        each['doctype'] = Doctypes.invoices
      }
      return each;
    })
  }

  checkedItems(event, item) {
    const temp = this.invoicesData.filter((each: any) => each.checked);
    this.selectAll = temp.length == this.invoicesData.length;
    this.dupinvoicesList = temp;
    this.dupinvoicesList = this.dupinvoicesList.map((each: any) => {
      if (each) {
        each['doctype'] = Doctypes.invoices
      }
      return each;
    })
  }

  goback() {
    this.router.navigate(['./clbs/summary-details/' + this.paramsID])
  }
  createSummaries() {
    let list = this.dupinvoicesList.map((each: any) => each.name)
    const quaryParams = { filters: [] }
    if (list.length) {
      quaryParams.filters.push(['parent', 'in', list])
    }
    console.log(JSON.stringify(quaryParams.filters))
    this.http.get(`${ApiUrls.createBreakUp}`, {
      params: {
        filters: JSON.stringify(quaryParams.filters),
        summary: this.paramsID
      }
    }).subscribe((res: any) => {
      if(res?.message?.success){
        this.toastr.success(res?.message?.message)
        this.router.navigate(['./clbs/summary-details/' + this.paramsID])
      }else{
        this.toastr.error(res?.message?.message)
      }
    })
  }

  updateRouterParams(){
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.search = JSON.stringify(temp.search);
    this.router.navigate([`${'clbs/invoices'}/${this.paramsID}`], {
      queryParams: temp
    });
  }

  addB2CEnableFn(){
    if(this.addB2CEnable){
      this.getB2CInvoices()
    }
  }
  getB2CInvoices(search=null){
    let queryParams = { filters: [['invoice_type', 'like', 'B2C'], ['irn_generated', 'like', 'Success'],['summary','like',null]] };
    if(search){
      queryParams.filters.push(['invoice_number','like',`%${search}%`])
    }
    if (this.filters.search.filterDate) {
      const filter = new DateToFilter('Invoices', 'Custom', this.filters.search.filterDate as any, 'invoice_date' as any).filter;
      if (filter) {
        queryParams.filters.push(filter);
      }
    }


    const resultApi = this.http.get(ApiUrls.invoices, { params: {
      fields : JSON.stringify(['*']),
      filters : JSON.stringify(queryParams.filters),
      limit_page_length : 'None'
    } });
     forkJoin([ resultApi]).subscribe((res:any)=>{
      console.log(res)
      if(res[0]?.data){
        this.b2cInvoiceList = res[0]?.data
      }else{
        this.toastr.error("")
      }
     })
  }

  b2cInvoiceSearch(b2cInvoice){
    this.onInvoiceSearch.emit(b2cInvoice.value);
  }

  inputfocus() {
    const element: any = document.getElementsByClassName('paragraphClass');
    element[0].style.display = "block";

  }
  inputblur() {
    const element: any = document.getElementsByClassName('paragraphClass');
    setTimeout(() => {
      element[0].style.display = "none";
    }, 400);

  }
  itemSelection(invoice){

    if (!window.confirm(`Are you want sure to add ${invoice?.invoice_number}?`)) {
      return null;
    }else{
      invoice['checked'] = false;
      this.invoicesData.push(invoice)
    }
   

  }
}

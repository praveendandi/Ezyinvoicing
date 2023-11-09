import { HttpClient } from '@angular/common/http';
import { Component, OnInit, EventEmitter } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { DateToFilter } from 'src/app/shared/date-filter'
import { environment } from 'src/environments/environment';

class InvoicesFilter {
  /**
   * Limit start of company filter
   * i.e Items per page
   */
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0
  active = 2;
  /**
   * Limit page length of company filter
   * page length
   */
  search = {
    filterBy: 'Today',
    filterDate: '',
    filterType: 'creation'
  };
}

@Component({
  selector: 'app-upload-invoices',
  templateUrl: './upload-invoices.component.html',
  styleUrls: ['./upload-invoices.component.scss']
})
export class UploadInvoicesComponent implements OnInit {

  filters = new InvoicesFilter();
  onSearch = new EventEmitter();
  invoicesStats = [];
  selectedInvoice;
  apiDomain = environment.apiDomain;
  active = 1;
  companyDetails;
  constructor(
    private http: HttpClient,
    private router: Router,
    private activatedRoute: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.getInvoiceList();
    // this.getInvoicesCount()
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page

  }

  getInvoicesCount(): void {
    this.http.get(ApiUrls.excelUploadInvoices, {
      params: {
        fields: JSON.stringify(["count( `tab"+Doctypes.excelUploadInvoices+"`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      this.filters.totalCount = res.data[0].total_count;
      this.getInvoiceList()
    })
  }

  getInvoiceList(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: InvoicesFilter) => {
      // this.filters.active = parseInt(params.active as any) || 2;
      const queryParams: any = { filters: [] };

      if (this.filters.search.filterBy) {
        if (this.filters.search.filterBy === 'Custom') {
          if (this.filters.search.filterDate) {
            const filter = new DateToFilter(Doctypes.excelUploadInvoices, this.filters.search.filterBy, this.filters.search.filterDate as any, this.filters.search.filterType as any).filter;
            if (filter) {
              queryParams.filters.push(filter);
            }
          }
        } else if (this.filters.search.filterBy !== 'All') {
          const filter = new DateToFilter(Doctypes.excelUploadInvoices, this.filters.search.filterBy, null, this.filters.search.filterType).filter;
          if (filter) {
            queryParams.filters.push(filter);
          }
        }
      }
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
      queryParams.fields = JSON.stringify(['name', 'process_time', 'uploaded_by', 'creation','invoice_details', 'referrence_file', 'gst_file']);
      queryParams.filters = JSON.stringify(queryParams.filters);
      queryParams.order_by = "`tabExcel upload Stats`.`creation` desc";
      const countApi = this.http.get(ApiUrls.excelUploadInvoices, {
        params: {
          fields: JSON.stringify(["count( `tabExcel upload Stats`.`name`) AS total_count"]),
          filters: queryParams.filters || []
        }
      });
      const resultApi = this.http.get(ApiUrls.excelUploadInvoices, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      if (data.data) {
        data.data = (data.data as any[]).map((each)=>{
          each.invoice_details = JSON.parse(each.invoice_details).invoice_details;
          return each;
        })

        data.data['checked'] = false;
        if (this.filters.currentPage !== 1) {
          this.invoicesStats = this.invoicesStats.concat(data.data)
        } else {
          this.invoicesStats = data.data;
        }
        console.log(this.invoicesStats)
      }
    });
  }
  navigateInvoices(data) {
    this.router.navigate(['home', 'invoices'], {
      queryParams: {
        search: JSON.stringify({
          uploadType: 'File',
          filterType: 'invoice_date',
          filterBy: 'Custom',
          filterDate: [new Date(data?.date), new Date(data?.date)]
        })
      }, queryParamsHandling: 'merge'
    })
  }



  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.search = JSON.stringify(temp.search);
    this.router.navigate(['home/upload-invoice'], {
      queryParams: temp
    });
  }

  print(invoice) {
    this.selectedInvoice = invoice
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = this.apiDomain + invoice?.invoice_file;
    document.body.appendChild(iframe);
    if (iframe.src) {
      setTimeout(() => { iframe.contentWindow.print() })
    }
  }

  checkPagination(): void {
    if (this.filters.itemsPerPage < this.invoicesStats.length) {
      this.filters.currentPage = 1
      this.updateRouterParams()
    } else {
      this.updateRouterParams()
    }
  }

  onDateFilterType() {
    this.updateRouterParams();
  }

  onDateFilterChange() {
    this.filters.currentPage = 1;
    if (this.filters.search.filterBy == 'Custom') {
      this.filters.search.filterDate = '';
    } else {
      this.updateRouterParams();
    }
  }
}

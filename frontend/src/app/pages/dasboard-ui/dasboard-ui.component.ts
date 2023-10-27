import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, OnInit } from '@angular/core';
import moment from 'moment';
import { ToastrService } from 'ngx-toastr';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { DateToFilter } from 'src/app/shared/date-filter';
import { environment } from 'src/environments/environment';
import { NgbPaginationModule } from '@ng-bootstrap/ng-bootstrap';
import { Router } from '@angular/router';
declare var $: any;
class InvoicesFilter {
  itemsPerPage = 1;
  currentPage = 1;
  totalCount = 0;
  start = 0
  active = 2;
}
@Component({
  selector: 'app-dasboard-ui',
  templateUrl: './dasboard-ui.component.html',
  styleUrls: ['./dasboard-ui.component.scss'],
})
export class DasboardUiComponent implements OnInit, AfterViewInit {
  filters = new InvoicesFilter();
  diskSpace;
  freeSpace;
  diskPercent;
  invoiceCount;
  creditInvoice: any = {};
  debitInvoice;
  taxInvoice;
  deltedfiles;
  invoiceReconciliation;
  invoiceStatistics;
  apiDomain = environment.apiDomain;
  creditinvoices: any = {};
  debitinvoices: any = {};
  taxinvoices: any = {};


  missingInvoices: any = {};
  dateFiltersList = [
    {
      label: 'Today',
      value: {
        fromdate: moment(new Date()).format('YYYY-MM-DD'),
        todate: moment(new Date()).format('YYYY-MM-DD')
      }
    },
    {
      label: 'Yesterday',
      value: {
        fromdate: moment(new Date()).subtract(1, 'day').format('YYYY-MM-DD'),
        todate: moment(new Date()).subtract(1, 'day').format('YYYY-MM-DD')
      }
    },
    {
      label: 'This Week',
      value: {
        fromdate: moment(new Date()).startOf('week').format('YYYY-MM-DD'),
        todate: moment(new Date()).format('YYYY-MM-DD')
      }
    },
    {
      label: 'Last Week',
      value: {
        fromdate: moment(new Date()).subtract(1, 'week').startOf('week').format('YYYY-MM-DD'),
        todate: moment(new Date()).subtract(1, 'week').endOf('week').format('YYYY-MM-DD')
      }
    },
    {
      label: 'This Month',
      value: {
        fromdate: moment(new Date()).startOf('month').format('YYYY-MM-DD'),
        todate: moment(new Date()).format('YYYY-MM-DD')
      }
    },
    {
      label: 'Last Month',
      value: {
        fromdate: moment(new Date()).subtract(1, 'month').startOf('month').format('YYYY-MM-DD'),
        todate: moment(new Date()).subtract(1, 'month').endOf('month').format('YYYY-MM-DD')
      }
    },
    {
      label: 'This Year',
      value: {
        fromdate: moment(new Date()).startOf('year').format('YYYY-MM-DD'),
        todate: moment(new Date()).format('YYYY-MM-DD')
      }
    },
    {
      label: 'Last Year',
      value: {
        fromdate: moment(new Date()).subtract(1, 'year').startOf('year').format('YYYY-MM-DD'),
        todate: moment(new Date()).subtract(1, 'year').endOf('year').format('YYYY-MM-DD')
      }
    },
  ];
  selectedDate = 0;
  GSTRDate = 0;
  dateForInvoice = 1;
  dateFilter;

  taxb2b = [];
  taxb2c = [];
  creditb2b = [];
  debitb2b = [];
  creditb2c = [];
  debitb2c = [];
  sacSummary = [];
  companyDetails: any = {};
  creditInvoiceLoader = false;
  progressbarLoader = false;
  missingInvoicesLoader = false;
  taxinvoicesLoader = false;
  taxb2bLoader = false;
  pending_IRN: any = []
  invoice_recn_count: any = []
  constructor(private http: HttpClient, private toastr: ToastrService, public pagination: NgbPaginationModule, private router: Router,) { }

  ngOnInit(): void {

    this.companyDetails = JSON.parse(localStorage.getItem('company'))

    this.companyDetails = JSON.parse(localStorage.getItem('company'))

    let today_date: any = moment(new Date()).format('YYYY-MM-DD')
    let date_expiry: any = moment(this.companyDetails?.e_invoice_missing_start_date).format('YYYY-MM-DD')
    if (this.companyDetails?.e_invoice_missing_date_feature && today_date >= date_expiry) {
      this.get_invoice_Counts_for_irn();
    } else {
      this.getGSTR();
    }

  }

  ngAfterViewInit(): void {
    this.getDiskSpace();
    this.getInvoiceCounts();
    this.getTotalCount();
    this.getInvoiceDetailsCount();
    this.getGSTR();
    this.getInvoiceReconcillation();
  }

  getDiskSpace() {
    this.progressbarLoader = true;
    this.http.get(ApiUrls.diskSpace).subscribe((response: any) => {
      this.progressbarLoader = false;
      if (response) {
        // console.log(response?.message[1]);
        // console.log(response?.message[1].split(' '));
        const data = response?.message[1]?.split(' ');
        let filtered = data?.filter((item) => item);

        // console.log(filtered);
        if (filtered?.length) {
          this.diskSpace = filtered[1];
          this.freeSpace = filtered[3];
          const percentage = filtered[4].split('%');
          this.diskPercent = percentage[0];
        }

        // console.log(this.diskPercent);
      }
    });
  }

  getInvoiceCounts() {
    this.creditInvoiceLoader = true;
    this.http.get(ApiUrls.totalCount).subscribe((response: any) => {
      this.creditInvoiceLoader = false;
      if (response?.message?.data) {
        // console.log("count ======",response.message.data);
        const invoices = response.message.data;

        this.creditInvoice = invoices.reduce((prev, nxt) => {
          prev[nxt['invoice_category']] = nxt.count;
          return prev;
        }, {});

        // console.log(this.creditInvoice);
      }
    });
  }

  getTotalCount(): void {
    this.http
      .get(`${ApiUrls.resource}/${Doctypes.deleteDocument}`)
      .subscribe((res: any) => {
        // console.log(res);
        this.deltedfiles = res.data.length;
      });
  }


  getInvoiceDetailsCount() {
    // console.log(this.selectedDate);
    this.taxinvoicesLoader = true;
    this.http
      .post(ApiUrls.invoiceDetailsCount, {
        data: this.dateFiltersList[this.selectedDate].value,
      })
      .subscribe((response: any) => {
        this.taxinvoicesLoader = false;
        if (response) {
          const creditInvoices = response.message.data.creditinvoices;
          const debitInvoices = response.message.data.debitinvoices;
          const taxInvoices = response.message.data.invoices;
          this.creditinvoices = creditInvoices.reduce((prev, nxt) => {
            prev[nxt['irn_generated']] = nxt.count;
            return prev;
          }, {});
          this.debitinvoices = debitInvoices.reduce((prev, nxt) => {
            prev[nxt['irn_generated']] = nxt.count;
            return prev;
          }, {});
          this.taxinvoices = taxInvoices.reduce((prev, nxt) => {
            prev[nxt['irn_generated']] = nxt.count;
            return prev;
          }, {});
        }
      });
  }

  getGSTR() {
    this.taxb2bLoader = true;
    this.http
      .post(ApiUrls.gstrStatistics, {
        data: this.dateFiltersList[this.GSTRDate].value,
      })
      .subscribe((response: any) => {
        this.taxb2bLoader = false;
        if (response) {
          //  console.log(response)
          this.taxb2b = response.message.data?.taxb2b;
          this.taxb2c = response.message.data?.taxb2c;
          this.creditb2b = response.message.data?.creditb2b;
          this.debitb2b = response.message.data?.debitb2b;
          this.debitb2c = response.message.data?.debitb2c;
          this.creditb2c = response.message.data?.creditb2c;
          this.sacSummary = response.message.data?.sacSummary;
        }
      });
  }


  getInvoiceReconcillation() {
    this.missingInvoicesLoader = true;
    this.http.post(ApiUrls.invoiceReconsiliationCount, {
      data: this.dateFiltersList[this.dateForInvoice].value,
    }).subscribe((response: any) => {
      this.missingInvoicesLoader = false;
      if (response) {
        this.invoiceReconciliation = response.message?.data;

        // console.log(this.invoiceReconciliation);
        this.missingInvoices = this.invoiceReconciliation?.ezydata.reduce((prev, nxt) => {
          prev[nxt['invoice_found']] = nxt.count;
          return prev;
        }, {});

        // console.log(this.missingInvoices);
      }
    })
  }

  notAvailable() {
    this.toastr.error("Not Available now")
  }
  downloadgstr1() {
    let from = this.dateFiltersList[this.GSTRDate].value.fromdate;
    let to = this.dateFiltersList[this.GSTRDate].value.todate
    let dataObj = {
      data: {
        ...this.dateFiltersList[this.GSTRDate].value, company: this.companyDetails.name
      }
    }

    this.http.post(ApiUrls.dowloadGSTR1, dataObj).subscribe((res: any) => {
      if (res?.message) {
        let path = res?.message.replace(/(.*)\/.*(\.xlsx$)/i, `${'GSTR1REPORT'}${from.replace('-', '').replace('-', '')}-${to.replace('-', '').replace('-', '')}$2`)
        console.log(path);
        var link = document.createElement('a');
        link.href = `${this.apiDomain}${res.message}`;
        link.download = path;
        link.target = "_blank";
        link.click()
        // window.open(`${this.apiDomain}${res.message}`, "_blank");

      }
    })
  }

  download(filename, text) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
  }

  // Start file download.


  get_invoice_Counts_for_irn() {
    this.http.get(ApiUrls.missing_irn_generation).subscribe((res: any) => {
      if (res?.message.length) {
        this.pending_IRN = res?.message
        this.invoice_recn_count = this.pending_IRN.map((each: any, index = 1) => {
          console.log(each)
          each['idx'] = index + 1
          return each;
        })
        this.pending_IRN = this.pending_IRN.filter((each: any) => {
          if (each?.idx <= 8) {
            return each
          }
        })
      } else {
        this.toastr.error("Error Occured")
      }
    })
  }
  downloadReport() {
    this.http.post(ApiUrls.report_for_invoices, { report_type: 'due_in' }).subscribe((res: any) => {
      if (res?.message?.success) {
        window.open(`${this.apiDomain}${res?.message?.file_path}`, "_blank");
      }
    })
  }


}

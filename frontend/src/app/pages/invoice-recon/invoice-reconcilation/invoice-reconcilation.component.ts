import { Location } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, ChangeDetectionStrategy, ChangeDetectorRef, AfterViewInit, ElementRef, ViewChild, EventEmitter } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiUrls } from 'src/app/shared/api-urls';
import Stepper from 'bs-stepper';
import { ToastrService } from 'ngx-toastr';
import moment from 'moment';
import { DateTimeAdapter } from 'ng-pick-datetime';
import { environment } from 'src/environments/environment';
import { MonthYearService } from 'src/app/shared/services/month-year.service';
import { debounceTime, takeUntil } from 'rxjs/operators';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

class InvoicesFilter {
  name = '';
  doctype = 'Invoice Count';
  startDate = '';
  endDate = '';
  search = {
    invoice_number: '',
    invoice_type: '',
    invoice_date: '',
    sac_code: '',
    baseamountstatus: '',
    invoice_amount_status: ''
  };
}
@Component({
  selector: 'app-invoice-reconcilation',
  templateUrl: './invoice-reconcilation.component.html',
  styleUrls: ['./invoice-reconcilation.component.scss']
})
export class InvoiceReconcilationComponent implements OnInit {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  public onSearch = new EventEmitter()
  @ViewChild('widgetsContent') widgetsContent: ElementRef;
  filters = new InvoicesFilter();
  reconcilData: any = {};
  private stepper: Stepper;
  fromMaxDate = new Date()
  toMaxDate = new Date()
  toMinDate = new Date(this.toMaxDate.getFullYear(), this.toMaxDate.getMonth(), 1)
  fromDate = [new Date(this.toMaxDate.getFullYear(), this.toMaxDate.getMonth(), 1), null];
  toDate = [null, this.toMaxDate]
  apiDomain = environment.apiDomain;
  hsn_summary = 'all'
  monthList: any;
  yearsList: any;

  barchart1 = {
    type: "BarChart",
    data: [
      ["", 0, '#6AA1F3', 'Invoice Count (0)'],
      ["", 0, '#6AA1F3', 'Missing  (0)']
    ],
    columnNames: ['', 'Count', { role: 'style' }, { role: "annotation" }],
    options: {
      annotations: {
        textStyle: {
          // fontName: 'Times-Roman',
          fontSize: 13,
          bold: true,
          italic: false,
          // The color of the text.
          color: '#fff',
          // The color of the text outline.
          auraColor: '#d799ae',
          // The transparency of the text.
          opacity: 1
        },
      },
      width: 320,
      height: 220,
      bar: { groupWidth: '50%' },
      hAxis: {
        title: 'Year',
        direction: -1,
        slantedTextAngle: 90 // here you can even use 180
      },
      vAxis: {
        minValue: 0
      },
      isStacked: true,
      chartArea: {
        height: '10%',
        width: '10%',
        top: 10,
        right: 20,
        bottom: 10,
        left: 10
      },
      legend: { position: 'none' },
    },
  }

  barchart2 = {
    type: "BarChart",
    data: [
      ["", 0, 'Invoice Count (0)'],
      ["", 0, 'Missing (0)']
    ],
    columnNames: ['', 'Count', { role: "annotation" }],
    options: {
      width: 320,
      height: 220,
      hAxis: {
        title: 'Year'
      },
      vAxis: {
        minValue: 0
      },
      isStacked: true,
      chartArea: {
        height: '10%',
        width: '10%',
        top: 10,
        right: 20,
        bottom: 10,
        left: 10
      },
      legend: { position: 'none' },
      bar: { groupWidth: '50%' },
      annotations: {
        textStyle: {
          // fontName: 'Times-Roman',
          fontSize: 13,
          bold: true,
          italic: false,
          // The color of the text.
          color: '#fff',
          // The color of the text outline.
          auraColor: '#d799ae',
          // The transparency of the text.
          opacity: 1
        },
      },

    },
  }
  footerTotalData: any;
  companyDetails: any;

  docTypeList = {
    invoice_count: 'Invoice Count',
    missing_in_opera: 'Missing in Opera',
    zero_invoice: 'Zero Invoice',
    missing_in_ezyInvoicing: 'Missing in EzyInvoicing',
    invoice_type_missmatch: 'Invoice Type Missmatch',
    recon_opera_comparison: 'Recon Opera Comparison',
    converted_b2b_to_b2c: 'Converted B2B to B2C',
    converted_b2c_to_b2b: 'Converted B2C to B2B',
    recon_hsn_summary: 'Recon HSN Summary',
    b2b_hsn_summary: 'B2B HSN Summary',
    b2c_hsn_summary: 'B2C HSN Summary',
    amendments:'Amendments',
    no_sac: 'No Sac'
  }
  totalSatasticsLabel = {
    invoice_amount: "Total Invoice Amt",
    total_invoice_amount:"Total Invoice Amt",
    total_tax_amount: "Total Taxable Amt",
    igst_amount: "Total IGST Amt",
    sgst_amount: "Total SGST Amt",
    cgst_amount: "Total CGST Amt",
    total_gst_amount: "Total GST Amt",
    other_charges: "Other Charges",
    cess: "Total CESS Amt",
    vat_amount: "Total VAT Amt",
    total_quantity: "Total Quantity",
    state_cess_amount: "Total State CESS Amt",
    central_cess_amount: "Total Central CESS Amt",
    ezyinvoicingbaseamount: "Ezy Invoicing Base Amt",
    operabaseamount: "Opera Base Amt",
    basemissmatchamount: "Base Missmatch Amount",
    ezyinvoicinginvoiceamount: "Ezy Invoicing Invoice Amt",
    operainvoiceamount: "Opera Invoice Amt",
    invoicemissmatchamount: "Invoice Missmatch Amt",
    before_gst: 'Before GST'
  }
  selectedTab: any = 'Invoice Count';
  // startDate: any;
  endDate: any;
  totalDashboardData: any;
  chartStatus: boolean;
  startDate: any;
  totalRecordsCount: any;
  constructor(
    private router: Router,
    public modal: NgbModal,
    private location: Location,
    private http: HttpClient,
    public dateTimeAdapter: DateTimeAdapter<any>,
    public activatedRoute: ActivatedRoute,
    public toastr: ToastrService,
    private yearService: MonthYearService,
    private cdr: ChangeDetectorRef
  ) {
    dateTimeAdapter.setLocale('en-IN');
  }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'));
    this.yearService.years.pipe(takeUntil(this.destroyEvents))
      .subscribe((data) => this.yearsList = data);

    this.yearService.months.pipe(takeUntil(this.destroyEvents))
      .subscribe((data) => this.monthList = data);
    this.stepper = new Stepper(document.querySelector('#stepper1'), {
      linear: false,
      animation: true
    })

    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
     console.log(res)
      this.updateRouterParams()
    });
    this.activatedRoute.queryParams.subscribe((res: any) => {
      this.startDate = res?.startDate
      this.endDate = res?.endDate
      this.filters.name = res?.name
      this.filters.startDate = res?.startDate
      this.filters.endDate = res?.endDate
      if (res?.doctype) {
        this.filters.doctype = res?.doctype
      }
      this.getReconData(this.filters.doctype)
    })

    this.getDashboardData()
  }

  getReconData(doctype) {
    let queryParams = {}
    if (this.filters.search.invoice_date) {
      queryParams['invoice_date'] = moment(this.filters.search.invoice_date).format('yyyy-MM-DD')
    }
    if (this.filters.search.invoice_number) {
      queryParams['invoice_number'] = ["like",`%${this.filters.search.invoice_number}%`]
    }
    if (this.filters.search.sac_code) {
      queryParams['sac_code'] = ["like",`%${this.filters.search.sac_code}%`]
    }

    if (this.filters.search.invoice_amount_status) {
      queryParams['invoice_amount_status'] = this.filters.search.invoice_amount_status
    }
    if (this.filters.search.invoice_type) {
      let data
      if (this.filters.search.invoice_type == 'all') {
        data = ["in", ['b2b', 'b2c']]
      } else {
        data = ["in", [this.filters.search.invoice_type]]
      }
      queryParams['invoice_type'] = data
    }

    if (this.filters.search.baseamountstatus) {
      let data
      if (this.filters.search.baseamountstatus == 'all') {
        data = ["in", ['MisMatch', 'Match','Missing In Opera']]
      } else {
        data = ["in", [this.filters.search.baseamountstatus]]
      }
      queryParams['baseamountstatus'] = data
    }
    let result = new Promise((resolve, reject) => {
      let data = {
        doctype: doctype,
        reconID: this.filters.name,
        export: false,
        filter: queryParams
      }
      this.http.post(`${ApiUrls.export_recon}`, data).subscribe((res: any) => {
        let key
        if (res?.message?.success) {
          key = Object.keys(this.docTypeList).find(k => this.docTypeList[k] === doctype);
          this.reconcilData[key] = res?.message?.data
          this.totalRecordsCount = res?.message?.counts?.count
          resolve(this.reconcilData)
        } else {
          resolve(false)
        }
        if (key) {
          let totalSatistics = this.reconcilData[key][this.reconcilData[key].length - 1]
          this.footerTotalData = this.convertObjToArr(totalSatistics)
        } else {
          this.footerTotalData = []
        }
      })
    })
    return result
  }
  getDashboardData() {
    this.chartStatus = false
    this.http.get(ApiUrls.invoice_recon_dashboard, {
      params: {
        recon_id: this.filters.name
      }
    }).subscribe((res: any) => {
      console.log(res)
      if (res?.message?.success) {
        this.chartStatus = true
        this.totalDashboardData = res?.message?.data
        this.barchart1.data[0][1] = this.totalDashboardData?.invoice_count?.ezyinvoicing_count
        this.barchart1.data[1][1] = this.totalDashboardData?.invoice_count?.missing_in_ezyinvoicing
        this.barchart1.data[0][3] = 'Invoice Count (' + this.totalDashboardData?.invoice_count?.ezyinvoicing_count + ')'
        this.barchart1.data[1][3] = 'Missing (' + this.totalDashboardData?.invoice_count?.missing_in_ezyinvoicing + ')'

        this.barchart2.data[0][1] = this.totalDashboardData?.invoice_count?.opera_folio_count
        this.barchart2.data[1][1] = this.totalDashboardData?.invoice_count?.missing_in_opera
        this.barchart2.data[0][2] = 'Invoice Count (' + this.totalDashboardData?.invoice_count?.opera_folio_count + ')'
        this.barchart2.data[1][2] = 'Missing (' + this.totalDashboardData?.invoice_count?.missing_in_opera + ')'
      } else {
        this.toastr.error(res?.message?.message)
      }
      this.setMatchingResult()
    })
  }

  customDates(toDate) {
    let range = new Date(toDate[0]).getDate() + '-' + new Date(toDate[1]).getDate()
    return range
  }

  changeTabs(doctype) {
    this.totalRecordsCount = null
    this.filters.doctype = doctype
    this.selectedTab = doctype
    this.resetFilters()
    this.getReconData(doctype).then((res: any) => {
      if (!res) {
        return
      }
      let key
      if (doctype == this.docTypeList.missing_in_opera && res?.missing_in_opera) {
        key = Object.keys(this.docTypeList).find(k => this.docTypeList[k] === this.docTypeList.missing_in_opera);
      }
      if (doctype == this.docTypeList.zero_invoice && res?.zero_invoice) {
        key = Object.keys(this.docTypeList).find(k => this.docTypeList[k] === this.docTypeList.zero_invoice);
      }
      if (doctype == this.docTypeList.recon_opera_comparison && res?.recon_opera_comparison) {
        key = Object.keys(this.docTypeList).find(k => this.docTypeList[k] === this.docTypeList.recon_opera_comparison);
      }
      if (doctype == this.docTypeList.recon_hsn_summary && res?.recon_hsn_summary) {
        key = Object.keys(this.docTypeList).find(k => this.docTypeList[k] === this.docTypeList.recon_hsn_summary);
      }
      if (doctype == this.docTypeList.no_sac && res?.no_sac) {
        key = Object.keys(this.docTypeList).find(k => this.docTypeList[k] === this.docTypeList.no_sac);
      }
      if (key) {
        let totalSatistics = this.reconcilData[key][this.reconcilData[key].length - 1]
        this.footerTotalData = this.convertObjToArr(totalSatistics)
      } else {
        this.footerTotalData = []
      }


    })
    if (this.selectedTab == this.docTypeList.invoice_count) {
      this.getDashboardData()
    }
  }

  scrollLeft() {
    console.log('sjdkjd')
    this.widgetsContent.nativeElement.scrollLeft -= 150;
  }

  scrollRight() {
    this.widgetsContent.nativeElement.scrollLeft += 150;
  }

  exportRecon() {
    if (!(this.fromDate[0] && this.toDate[1])) {
      this.toastr.warning('Select Dates')
      return
    }
    let fromDate = this.fromDate[0]
    let toData = this.toDate[1];
    this.http.get(ApiUrls.workbook_export, {
      params: {
        reconID: this.filters.name
      }
    }).subscribe((res: any) => {
      if (res.message.success) {
        const link = document.createElement('a');
        link.setAttribute('target', '_blank');
        link.setAttribute('href', this.apiDomain + res.message.file_url);
        link.setAttribute('download', res.message.file_name);
        link.click();
        link.remove();
      }
    })
  }
  async changeHSN_type(hsn_summary) {
    let key
    if (hsn_summary == 'all') {
      this.filters.doctype = this.docTypeList.recon_hsn_summary
      this.getReconData(this.docTypeList.recon_hsn_summary).then((res: any) => {
        if (res?.recon_hsn_summary) {
          key = Object.keys(this.docTypeList).find(k => this.docTypeList[k] == this.docTypeList.recon_hsn_summary);
          this.setFooterData(key)
        }
      })
    } else if (hsn_summary == 'b2b') {
      this.filters.doctype = this.docTypeList.b2b_hsn_summary
      this.getReconData(this.docTypeList.b2b_hsn_summary).then((res: any) => {
        if (res?.b2b_hsn_summary) {
          key = Object.keys(this.docTypeList).find(k => this.docTypeList[k] == this.docTypeList.b2b_hsn_summary);
          this.setFooterData(key)
        }
      })
    } else if (hsn_summary == 'b2c') {
      this.filters.doctype = this.docTypeList.b2c_hsn_summary
      this.getReconData(this.docTypeList.b2c_hsn_summary).then((res: any) => {
        if (res?.b2c_hsn_summary) {
          key = Object.keys(this.docTypeList).find(k => this.docTypeList[k] == this.docTypeList.b2c_hsn_summary);
          this.setFooterData(key)
        }
      })
    }
  }
  setFooterData(key) {
    if (key) {
      let totalSatistics = this.reconcilData[key][this.reconcilData[key].length - 1]
      this.footerTotalData = this.convertObjToArr(totalSatistics)
    } else {
      this.footerTotalData = []
    }
  }
  exportIndividually(doctype) {
    let queryParams = {}
    if (this.filters.search.invoice_date) {
      queryParams['invoice_date'] = this.filters.search.invoice_date
    }
    if (this.filters.search.invoice_number) {
      queryParams['invoice_number'] = ["like",`%${this.filters.search.invoice_number}%`]
    }
    if (this.filters.search.sac_code) {
      queryParams['sac_code'] = ["like",`%${this.filters.search.sac_code}%`]
    }

    if (this.filters.search.invoice_amount_status) {
      queryParams['invoice_amount_status'] = this.filters.search.invoice_amount_status
    }
    if (this.filters.search.invoice_type) {
      let data
      if (this.filters.search.invoice_type == 'all') {
        data = ["in", ['b2b', 'b2c']]
      } else {
        data = ["in", [this.filters.search.invoice_type]]
      }
      queryParams['invoice_type'] = data
    }

    if (this.filters.search.baseamountstatus) {
      let data
      if (this.filters.search.baseamountstatus == 'all') {
        data = ["in", ['MisMatch', 'Match','Missing In Opera']]
      } else {
        data = ["in", [this.filters.search.baseamountstatus]]
      }
      queryParams['baseamountstatus'] = data
    }
    let data = {
      doctype: doctype,
      reconID: this.filters.name,
      export: 'True',
      filter: queryParams
    }
    this.http.post(`${ApiUrls.export_recon}`, data).subscribe((res: any) => {
      console.log(res)
      if (res?.message?.success) {
        let key = Object.keys(this.docTypeList).find(k => this.docTypeList[k] === doctype);
        console.log(this.reconcilData)
        const link = document.createElement('a');
        link.setAttribute('target', '_blank');
        link.setAttribute('href', this.apiDomain + res.message.file_url);
        link.setAttribute('download', res.message.file_name);
        link.click();
        link.remove();
      }
    })
  }

  back() {
    let select_year : any = new Date(this.startDate).getFullYear()
    let select_month :any = new Date(this.startDate).getMonth() + 1
      if (select_month <= 9) {
        select_month = select_month ? `${0}${select_month}`:`${0}${new Date(this.startDate).getMonth() + 1}`;
      } else {
        select_month = select_month ? `${select_month}`:`${new Date(this.startDate).getMonth() + 1}`;
      }

    this.router.navigate(['home/invoice-recon'], {
      queryParams: {
        month: select_month,
        year: select_year
      }
    });
  }
  convertObjToArr(objData) {
    let arr = []
    if (!objData) {
      return
    }
    for (const [key, value] of Object.entries(objData)) {
      let data = {
        label: `${key}`,
        value: `${value}`
      }
      if (key != "gst_rate" && key != "total_quantity") {
        arr.push(data)
      }
    }
    return arr
  }

  fixedFooterStatus() {
    if ((this.selectedTab == this.docTypeList.missing_in_opera
      || this.selectedTab == this.docTypeList.zero_invoice
      || this.selectedTab == this.docTypeList.recon_opera_comparison
      || this.selectedTab == this.docTypeList.recon_hsn_summary
      || this.selectedTab == this.docTypeList.b2b_hsn_summary
      || this.selectedTab == this.docTypeList.b2c_hsn_summary
      || this.selectedTab == this.docTypeList.no_sac) && this.footerTotalData
    ) {
      return true
    } else {
      return false
    }
  }
  updateRouterParams(): void {
    console.log("++++++++++++++++++++")
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.search = JSON.stringify(temp.search);
    this.router.navigate(['home/invoice-recon/invoice-recon'], {
      queryParams: temp
    });
  }

  setMatchingResult() {
    let circle = document.querySelector(".single-chart .circle");
    // circle.setAttribute('stroke-dasharray', '50, 100');
  }
  redoRecon() {
    this.http.get(ApiUrls.redo_recon, {
      params: {
        name: this.filters.name
      }
    }).subscribe((res: any) => {
      console.log(res)
      if (res.message.success) {
        this.toastr.success(res?.message?.message)
        this.modal.dismissAll()
      } else {
        this.toastr.error(res?.message?.message)
      }
    })
  }

  redoRecon_modal(redo_recon) {
    this.modal.open(redo_recon, { size: 'md', centered: true })
  }

  resetFilters() {
    let invoice_type = 'all'
    if (this.selectedTab != this.docTypeList.missing_in_opera
      && this.selectedTab != this.docTypeList.zero_invoice
    ) {
      invoice_type = ''
    }

    let baseamountstatus='all'
    if (this.selectedTab != this.docTypeList.recon_opera_comparison) {
      baseamountstatus = ''
    }
    this.filters.search = {
      invoice_number: '',
      invoice_type: invoice_type,
      invoice_date: '',
      sac_code: '',
      baseamountstatus: baseamountstatus,
      invoice_amount_status: ''
    }
  }
}



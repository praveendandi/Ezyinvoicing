import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, EventEmitter, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import * as Moment from 'moment';
import moment from 'moment';
import { stateCode } from 'src/app/shared/state-codes';
import { CreateInvoiceManualComponent } from 'src/app/shared/models/create-invoice-manual/create-invoice-manual.component';
import { DateToFilter } from 'src/app/shared/date-filter'


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
    has_credit_items: '',
    filterType: 'creation',
    synced_to_erp: '',
    invoice_date: ''
  };
}


@Component({
  selector: 'app-manual-credit-notes',
  templateUrl: './manual-credit-notes.component.html',
  styleUrls: ['./manual-credit-notes.component.scss']
})
export class ManualCreditNotesComponent implements OnInit, OnDestroy {
  manualType;
  filters = new InvoicesFilter();
  onSearch = new EventEmitter();
  // gstNumber;
  // userData;
  companyDetails;
  // gstNumberError = false;
  // taxDetails = false;
  // creditInvoice: any = {}
  // taxPayerDetails: any = {};
  invoicesList = [];
  stateCodes;
  selectedMonth = moment(new Date()).format('MMM')
  selectedyear = 2022;
  years = [];

  // apiMethod;
  // place_of_supply;
  // today_date = Moment(new Date()).format('YYYY-MM-DD');

  @ViewChild('addCredit') addCredit: ElementRef;
  selectAll: any = false;
  dupinvoicesList: any[];
  gerenateIRNITems: boolean = false;
  constructor(private router: Router, private modal: NgbModal, private http: HttpClient, private activatedRoute: ActivatedRoute, private toastr: ToastrService) { }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page
    this.stateCodes = stateCode
    this.activatedRoute.queryParams.subscribe((res: any) => { this.manualType = res.type, this.filters.search.filterBy = res.filterBy || 'Today' })

    if (this.activatedRoute.snapshot.queryParams.invoice_date) {
      this.filters.search.invoice_date = this.activatedRoute.snapshot.queryParams.invoice_date;
      this.filters.search.filterBy = "All";
      this.filters.search.invoiceType = this.activatedRoute.snapshot.queryParams.invoiceType
      this.filters.search.irn = this.activatedRoute.snapshot.queryParams.irn_generated;
    }
    if (this.activatedRoute.snapshot.queryParams.irn_generated) {
      this.filters.search.irn = this.activatedRoute.snapshot.queryParams.irn_generated;
    }
    // this.userData = JSON.parse(localStorage.getItem('login'))

    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.invoicesList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });

    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res.search) {
        const dateBy = JSON.parse(res.search)
        this.filters.search.filterBy = dateBy.filterBy;
        this.filters.search.filterType = dateBy.filterType;
        this.filters.search.irn = dateBy.irn;
        this.filters.search.confirmation = dateBy.confirmation;
        this.filters.search.gstNumber = dateBy.gstNumber;
        this.filters.search.roomNo = dateBy.roomNo;
        this.filters.search.name = dateBy.name;
        this.filters.search.invoice = dateBy.invoice;
        this.filters.search.synced_to_erp = dateBy.synced_to_erp;
      }
    })

    this.getInvoiceList();
    this.getYear()
  }

  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.type = this.manualType
    temp.search = JSON.stringify(temp.search);
    this.router.navigate(['home/manual-credit-notes'], {
      queryParams: temp,
    });
  }

  getInvoicesCount(): void {
    this.http.get(ApiUrls.invoices, {
      params: {
        fields: JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      this.filters.totalCount = res.data[0].total_count;
      this.getInvoiceList()
    })
  }

  getInvoiceList(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: InvoicesFilter) => {
      this.filters.active = parseInt(params.active as any) || 2;
      const queryParams: any = { filters: [] };

      if (this.filters.search.confirmation) {
        queryParams.filters.push(['confirmation_number', 'like', `%${this.filters.search.confirmation}%`]);
      }
      if (this.filters.search.invoice) {
        queryParams.filters.push(['invoice_number', 'like', `%${this.filters.search.invoice}%`]);
      }
      if (this.filters.search.gstNumber) {
        queryParams.filters.push(['gst_number', 'like', `%${this.filters.search.gstNumber}%`]);
      }
      if (this.filters.search.invoiceType) {
        queryParams.filters.push(['invoice_type', '=', this.filters.search.invoiceType]);
      }
      if (this.filters.search.irn) {
        queryParams.filters.push(['irn_generated', 'in', this.filters.search.irn]);
      }
      if (this.filters.search.name) {
        queryParams.filters.push(['guest_name', 'like', `%${this.filters.search.name}%`]);
      }
      if (this.filters.search.roomNo) {
        queryParams.filters.push(['room_number', 'like', `%${this.filters.search.roomNo}%`]);
      }
      if (this.filters.search.has_credit_items) {
        queryParams.filters.push(['has_credit_items', 'like', `%${this.filters.search.has_credit_items}%`]);
      }
      if (this.filters.search.synced_to_erp) {
        queryParams.filters.push(['synced_to_erp', 'like', `%${this.filters.search.synced_to_erp}%`]);
      }
      if (this.filters.search.sortBy) {
        queryParams.order_by = '`tabInvoices`.`' + this.filters.search.sortBy + '` ' + this.filters.search.orderBy + '';
      }
      if (this.filters.search.invoice_date) {
        queryParams.filters.push(['invoice_date', '=', `${this.filters.search.invoice_date}`]);
      }

      if (this.filters.search.filterBy) {

        if (this.filters.search.filterBy === 'Custom') {
          if (this.filters.search.filterDate) {
            const filter = new DateToFilter('Invoices', this.filters.search.filterBy, this.filters.search.filterDate as any, this.filters.search.filterType as any).filter;
            if (filter) {
              queryParams.filters.push(filter);
            }
          }
        } else if (this.filters.search.filterBy !== 'All') {
          const filter = new DateToFilter('Invoices', this.filters.search.filterBy, null, this.filters.search.filterType as any).filter;
          if (filter) {
            queryParams.filters.push(filter);
          }
        }

      }
      if (this.manualType === 'Credit') {
        queryParams.filters.push(['invoice_category', '=', 'Credit Invoice']);
      }
      if (this.manualType === 'Debit') {
        queryParams.filters.push(['invoice_category', '=', 'Debit Invoice']);
      }
      if (this.manualType === 'Tax') {
        queryParams.filters.push(['invoice_category', '=', 'Tax Invoice']);
        queryParams.filters.push(['invoice_from', '=', 'Web']);
      }

      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.limit_start = this.filters.start;
      queryParams.fields = JSON.stringify(['*']);
      // queryParams.filters.push(['invoice_from', '=', 'Web']);
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
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.invoicesList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      this.selectAll = false;
      this.dupinvoicesList = []
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.invoicesList.length + index + 1;

          let today_date: any = Moment(each?.invoice_date).format('YYYY-MM-DD')
          let date_expiry: any = this.companyDetails?.einvoice_missing_start_date ? Moment(this.companyDetails?.einvoice_missing_start_date).format('YYYY-MM-DD') : null
          if (this.companyDetails?.einvoice_missing_date_feature && today_date >= date_expiry) {
            let today_date: any = Moment(new Date()).format('YYYY-MM-DD')
            let date_expiry: any = Moment(Moment(each?.invoice_date).add(7, 'd').format('YYYY-MM-DD'))
            date_expiry = Moment(date_expiry).format('YYYY-MM-DD')
              each['expiry_date'] = Moment(date_expiry).format('YYYY-MM-DD')
              each['expiry_days'] = Moment(date_expiry).diff(Moment(today_date), 'days')
            
          }
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
  addManualCredit() {
    // this.taxPayerDetails = {};
    // this.creditInvoice = {};
    // this.modal.open(this.addCredit, {
    //   size: 'lg',
    //   centered: true
    // });
    this.modal.open(CreateInvoiceManualComponent, {
      size: 'lg',
      centered: true
    })
  }

  checkedItemsAll(event) {
    if (this.selectAll) {
      this.dupinvoicesList = this.invoicesList.filter((each: any) => {
        if (each.irn_generated == "Pending") {
          each.checked = true
        }
        return each;
      })
    } else {
      this.dupinvoicesList = this.invoicesList.filter((each: any) => {
        if (each.irn_generated == "Pending") {
          each.checked = false
        }
        return each;
      })
    }
    this.dupinvoicesList = this.invoicesList.filter((each: any) => each.checked)
    this.dupinvoicesList = this.dupinvoicesList.map((each: any) => {
      if (each) {
        each['doctype'] = Doctypes.invoices
      }
      return each;
    })
    console.log(this.dupinvoicesList)
  }
  checkedItems(event, item) {
    const temp = this.invoicesList.filter((each: any) => each.checked);
    this.selectAll = temp.length == this.invoicesList.length;
    this.dupinvoicesList = temp;
    this.dupinvoicesList = this.dupinvoicesList.map((each: any) => {
      if (each) {
        each['doctype'] = Doctypes.invoices
      }
      return each;
    })
    console.log(this.dupinvoicesList)
  }
  openModalIRN(multiGenerateIrn) {

    let modalData = this.modal.open(multiGenerateIrn, { centered: true, size: 'md' })
    modalData.result.then((res: any) => {
      if (res == 'generated') {
        this.dupinvoicesList = []
        this.gerenateIRNITems = false;
        this.getInvoiceList()
      }

    })
  }
  async generateIrn() {
    if (!window.confirm(`Are you sure to generate IRN? `)) {
      return null;
    } else {
      const apiCalls = this.dupinvoicesList.map((each: any, idx) => {

        return new Promise((resolve, reject) => {
          // this.dupinvoicesList[idx] = { uploadProgress: 0, parserProgress: 0, color: 'info', invoice_number: each.invoice_number,name: each.name };
          // const formData = new FormData();
          // formData.append('method', 'generateIrn');
          // formData.append('args', `{"invoice_number":"${each.name}"}`);
          // formData.append('docs', JSON.stringify(each));
          // this.http.post(ApiUrls.generateIrn, formData, {
          //   reportProgress: true, observe: "events",
          // }).subscribe(async (event: any) => {
          //   if (event.type === HttpEventType.UploadProgress) {
          //     this.dupinvoicesList[idx].uploadProgress = Math.round((100 * (event.loaded / event.total)));
          //   }
          //   if (event.type === HttpEventType.Response) {
          //     if (event.body.message.success) {
          //       this.dupinvoicesList[idx].color = 'success';
          //     } else {
          //       this.dupinvoicesList[idx].color = 'danger';
          //     }
          //   }

          this.dupinvoicesList[idx] = { uploaded: '', invoice_number: each.invoice_number, name: each.name, guest_name: each.guest_name };
          // const formData = new FormData();
          // formData.append('method', 'generateIrn');
          // formData.append('args', `{"invoice_number":"${each.name}"}`);
          // formData.append('docs', JSON.stringify(each));
          const dataObj = {
            invoice_number: each.name,
            generation_type: 'Manual'
          }
          this.http.post(ApiUrls.generateIrn_new, { data: dataObj }).subscribe(async (event: any) => {
            if (event.message.success) {
              this.dupinvoicesList[idx].uploaded = "success";
            } else {
              this.dupinvoicesList[idx].uploaded = "failed";
            }

          }, (err) => {
            resolve
            console.log('err: ', err);
          });
          resolve(idx)
        })

      })
      await Promise.all(apiCalls);
      this.gerenateIRNITems = true;

    }
  }
  ngOnDestroy() {
    this.dupinvoicesList = [];
    this.gerenateIRNITems = false;
    this.modal.dismissAll()
  }


  onDateFilterChange() {
    if (this.filters.search.filterBy == 'Custom') {
      this.filters.search.filterDate = '';
    } else {
      this.updateRouterParams();
    }
  }
  onDateFilterType() {
    this.updateRouterParams();
  }


  checkPagination(): void {
    // console.log(this.invoicesList.length)
    // if(this.filters.itemsPerPage < this.invoicesList.length){
    this.filters.currentPage = 1
    this.updateRouterParams()
    // }else{
    //   this.updateRouterParams()
    // }
  }

  openVideo(video) {
    this.modal.open(video, {
      size: 'xl',
      centered: true
    });
  }


  // synctoGst(){
  //   this.http.get(ApiUrls.bulk_sync_ezygst).subscribe((res: any) => {
  //     if (res.message.success) {
  //       this.toastr.success(res.message.message);
  //       this.getInvoiceList()
  //     } else {
  //       this.toastr.error(res.message.message)
  //     }
  //   })
  // }

  getYear() {
    var currentYear = new Date().getFullYear()
    var startYear = currentYear;
    for (var i = startYear; i <= currentYear; i++) {
      this.years.push(startYear++);
    }
    return this.years;
  }


  //  syncModel(content) {
  //     this.modal.open(content, {size:'md', centered: true,});
  //   }

}


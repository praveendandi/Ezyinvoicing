import { Component, EventEmitter, OnInit } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { DateTimeAdapter } from 'ng-pick-datetime';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import moment, * as Moment from 'moment';
import { ToastrService } from 'ngx-toastr';
import { MonthYearService } from 'src/app/shared/services/month-year.service';
import { debounceTime, takeUntil } from 'rxjs/operators';
import { NgForm } from '@angular/forms';
import { SocketService } from 'src/app/shared/services/socket.service';
import { merge } from 'rxjs';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-invoice-reconcilation-list',
  templateUrl: './invoice-reconcilation-list.component.html',
  styleUrls: ['./invoice-reconcilation-list.component.scss']
})
export class InvoiceReconcilationListComponent implements OnInit {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  onSearch = new EventEmitter();

  apiDomain = environment.apiDomain;
  reconcilData: any;
  hsn_final_data: any;
  companyDetails: any;
  fromMinDate: any;
  fromMaxDate = new Date()
  toMaxDate = new Date()
  toMinDate = new Date(this.toMaxDate.getFullYear(), this.toMaxDate.getMonth(), 1)
  fromDate = [new Date(this.toMaxDate.getFullYear(), this.toMaxDate.getMonth(), 1), null];
  toDate = [null, this.toMaxDate]
  summaryData: any = {}


  recon: any = false


  active: 1;
  filename;
  fileToUpload;
  signature_img: any = {}
  UserSignature: any = {};
  userName;
  years: any = [];
  filters: any = {
    selectedYear: '',
    selectedMonth: ''
  }
  b2bInvoicesData: any;
  days: any;
  dates: any = { from: '', to: '' }

  yearsList: any;
  monthList: any;
  reconDetails: any = [];
  month: any;
  year: any;
  dupreconDetails: any;
  selectAll: boolean = false;
  reconUnderProcessStatus: boolean=false;

  selectedFile = [];
  uploadedFile = false;

  constructor(
    public modal: NgbModal,
    public dateTimeAdapter: DateTimeAdapter<any>,
    public activatedRoute: ActivatedRoute,
    private http: HttpClient,
    public toastr: ToastrService,
    private router: Router,
    private yearService: MonthYearService,
    private socketService: SocketService
  ) {
    dateTimeAdapter.setLocale('en-IN');
  }

  ngOnInit(): void {

    this.socketService.connectMe()
    this.companyDetails = JSON.parse(localStorage.getItem('company'));
    this.yearService.years.pipe(takeUntil(this.destroyEvents))
      .subscribe((data) => this.yearsList = data);

    this.yearService.months.pipe(takeUntil(this.destroyEvents))
      .subscribe((data) => this.monthList = data);

      this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
        this.filters.start = 0;
        this.filters.totalCount = 0;
        this.updateRouterParams()
      });

      let current_date = new Date();
      let year_value = current_date.getFullYear()
      this.year = year_value
      
      let select_month  = current_date.getMonth() + 1
      if (select_month <= 9) {
        this.month = select_month ? `${0}${select_month}`:`${0}${current_date.getMonth() + 1}`;
      } else {
        this.month = select_month ? `${select_month}`:`${current_date.getMonth()+1}`;
      }
      console.log(this.month, "====",select_month)
    this.activatedRoute.queryParams.subscribe((res: any) => {
      // console.log(res)
      
      this.year = res?.year || this.year
      this.month = res?.month || this.month

      // if (res?.month <= 9) {
      //   this.month = res?.month ? `${0}${res?.month}`:`${0}${current_date.getMonth() + 1}`;
      // } else {
      //   this.month = res?.month ? `${res?.month}`:`${current_date.getMonth()+1}`;
      // }
      
      
      this.fromDateSelected(this.month, this.year)
      this.getReconDetails().then((res:any)=>{
        res.forEach(element => {
          if(element?.processing == 'Pending'){
            this.assignNewProcessingPercentage(element)
          }
        });
        // this.assignNewProcessingPercentage(data)
      })
      merge(this.socketService.newReCon.pipe(takeUntil(this.destroyEvents))).pipe(debounceTime(300)).subscribe((data:any) =>{
        if(data){
          // console.log("New Recon =========",data)
          this.reconUnderProcessStatus = false
          this.getReconDetails();
          this.selectMonthYear(this.month, this.year)
        }
      })
      merge(this.socketService.deleteReCon.pipe(takeUntil(this.destroyEvents))).pipe(debounceTime(300)).subscribe((data:any) =>{
        if(data){
          // console.log("delete Recon =========",data)
          this.selectMonthYear(this.month, this.year);
          this.getReconDetails()
        }
      })
      merge(this.socketService.newReConProcessing.pipe(takeUntil(this.destroyEvents))).pipe(debounceTime(300)).subscribe((data:any) =>{
        if(data){
          // console.log("newReConProcessing Recon =========",data)

          if(data?.percentage<=5){
            this.getReconDetails().then((res:any)=>{
              this.assignNewProcessingPercentage(data)
            })
          }else{
            this.assignNewProcessingPercentage(data)
          }
        }


        // this.selectMonthYear(this.month, this.year);
        // this.getReconDetails()
      })
    })



  }

  assignNewProcessingPercentage(data){
    this.reconDetails.forEach(element => {
      if(element?.name == data?.name || element?.processing == 'Pending'){
        element['recordStatus']='processing'
        element['percentage']=data?.percentage
        this.reconUnderProcessStatus = true
      }
    });
    // console.log('this.reconDetails',this.reconDetails)
  }
  reconSubmit() {
    this.recon = true
    this.modal.dismissAll();
  }

  invoiceReconcilation() {
    this.router.navigate(['/home/invoice-recon'])
  }


  daysInMonth(month: any, year: any) {
    return this.days = new Date(year, month, 0).getDate();
  }

  changeSelect(e: any, type: any) {
    let days = this.daysInMonth(this.filters.selectedMonth, this.filters.selectedYear);
    this.dates.from = `${this.filters.selectedYear}-${this.filters.selectedMonth}-01`;
    this.dates.to = `${this.filters.selectedYear}-${this.filters.selectedMonth}-${days}`
  }

  reconciliationModel(addRecon) {
    let modal = this.modal.open(addRecon, { size: 'md', centered: true })

  }

  fromDateSelected(month, year) {

    let today = new Date();
    let selectedDate = new Date(year, month - 1, 1)
    this.fromMinDate = selectedDate
    this.fromDate = [selectedDate, null];

    this.toMinDate = selectedDate

    let daysInMonth = new Date(year, month, 0).getDate();
    if (selectedDate.getMonth() + 1 == today.getMonth() + 1) {
      //  console.log('same month')
      this.toMaxDate = today
      this.toDate = [null, today];
      this.fromMaxDate = today

    } else {
      //  console.log('not same month')
      this.toMaxDate = new Date(year, month - 1, daysInMonth)
      this.toDate = [null, this.toMaxDate];
      this.fromMaxDate = this.toMaxDate

    }
    return true
  }
  dateChange() {
    if (this.fromDate[0] && this.toDate[1]) {
      if (this.fromDate[0].getDate() > this.toDate[1].getDate() || this.fromDate[0].getMonth() != this.toDate[1].getMonth()) {
        this.toDate = [null, null];
      }
    }
  }

  getReconcilationData(form: NgForm) {
    if (!(this.fromDate[0] && this.toDate[1])) {
      form.form.markAllAsTouched()
      return
    }

    let fromDate = this.fromDate[0]
    let toData = this.toDate[1];
    this.http.post(ApiUrls.create_reconciliation, {
      start_date: Moment(new Date(fromDate)).format('YYYY-MM-DD'),
      end_date: Moment(new Date(toData)).format('YYYY-MM-DD'),
    }).subscribe((res: any) => {
      if (res.message.success) {
        this.modal.dismissAll()
        this.getReconDetails()
      }else{
        this.toastr.error(res?.message?.message)
      }
    })
  }

  getReconDetails() {
    let result = new Promise((resolve,reject)=>{
      let from_date = moment(this.fromDate[0]).format('YYYY-MM-DD')
      let to_date = moment(this.toDate[1]).format('YYYY-MM-DD')
      this.http.get(`${ApiUrls.resource}/${Doctypes.reconDetails}`, {
        params: {
          fields: JSON.stringify(['*']),
          filters: JSON.stringify([['start_date', 'Between', [from_date, to_date]]])
        }
      }).subscribe((result: any) => {
        if (result?.data) {
          this.reconDetails = result?.data
          this.reconDetails = result?.data.map((each: any, index) => {
            if (each) {
              // each.index = this.invoicesData.length + index + 1;
              each['checked'] = false;
            }
            return each;
          })
          resolve(this.reconDetails)
        }else{
          this.toastr.error(result?.message?.message)
        }
      })
    })
    return result
  }
  selectMonthYear(month, year) {
    this.reconUnderProcessStatus = false
    this.month = month
    this.year = year
    this.updateRouterParams()

  }
  updateRouterParams(): void {
    let data = {
      month: this.month,
      year: this.year
    }
    this.router.navigate(['home/invoice-recon'], {
      queryParams: data
    });
  }


  checkedItemsAll(event) {
    if (this.selectAll) {
      this.dupreconDetails = this.reconDetails.filter((each: any) => {
        each.checked = true
        return each;
      })
    } else {
      this.dupreconDetails = this.reconDetails.filter((each: any) => {
        each.checked = false
        return each;
      })
    }
    this.dupreconDetails = this.reconDetails.filter((each: any) => each.checked)
    this.dupreconDetails = this.dupreconDetails.map((each: any) => {
      if (each) {
        each['doctype'] = Doctypes.invoices
      }
      return each;
    })
  }

  checkedItems(event, item) {
    const temp = this.reconDetails.filter((each: any) => each.checked);
    this.selectAll = temp.length == this.reconDetails.length;
    this.dupreconDetails = temp;
    this.dupreconDetails = this.dupreconDetails.map((each: any) => {
      if (each) {
        each['doctype'] = Doctypes.invoices
      }
      return each;
    })
  }
  checkSelection() {
    if(this.reconUnderProcessStatus){
      return true
    }
    return !this.reconDetails.some(res => res.checked)
  }
  checkDateForReconcile() {
    let today = new Date()
    let selectedDate = new Date(this.year, this.month - 1, 1)
    if (selectedDate > today) {
      return true
    } else {
      return false
    }
  }
  deleteReconData() {
    let deletingReconData = []
    this.dupreconDetails.filter((res: any) => {
      deletingReconData.push(res.name)
    })
    this.http.get(ApiUrls.delete_recon, {
      params: {
        name: JSON.stringify(deletingReconData)
      }
    }).subscribe((res: any) => {
      if (res.message.success) {
        // this.toastr.success(res?.message?.message)
        // this.selectMonthYear(this.month, this.year)
        this.updateRouterParams()
        this.modal.dismissAll()
      } else {
        this.toastr.error(res?.message?.message)
      }
    })

  }
  deleteReconModal(delete_recon) {
    this.modal.open(delete_recon, { size: 'md', centered: true })
  }
  redoRecon(name) {
    this.http.get(ApiUrls.redo_recon, {
      params: {
        name: name
      }
    }).subscribe((res: any) => {
      if (res.message.success) {
        // this.toastr.success(res?.message?.message)
        // this.selectMonthYear(this.month, this.year)
        this.updateRouterParams()
        this.modal.dismissAll()
      } else {
        this.modal.dismissAll()
        this.toastr.error(res?.message?.message)
      }
    })
  }
  redoRecon_modal(redo_recon) {
    this.modal.open(redo_recon, { size: 'md', centered: true })
  }

   /**openModelXml  */
   openModelXml(xmlUpload) {
    this.uploadedFile = false;
    this.selectedFile = [];
    let moadl = this.modal.open(xmlUpload, { centered: true, size: 'md', backdrop: 'static' })

    moadl.result.then((response: any) => {
      console.log("=========res ",response)
      if (response) {
        setTimeout((res: any) => {
          this.getReconDetails();
        }, 1000)
      }
    })
  }

  selectFiles(files) {
    this.uploadedFile = false;
    Array.from(files).forEach(file => {

      this.selectedFile.push({ progress: 0, file });
      // console.log("file=====",this.selectedFile)
    });
  }
  removeFromList(file, i) {
    this.selectedFile.splice(i, 1)
  }
  uploadFiles() {
    const formData = new FormData();
    formData.append('file', this.selectedFile[0].file);
    formData.append('is_private', '1');
    formData.append('folder', 'Home');
    // formData.append('doctype', Doctypes.invoiceReconciliation);
    // formData.append('fieldname', 'invoice');
    this.http.post(ApiUrls.uploadFile, formData,).subscribe((response: any) => {
      if (response.message) {

        this.http.post(ApiUrls.reconcilation, { file_list: response?.message?.file_url }).subscribe((res: any) => {
          if (res?.message) {
            this.uploadedFile = true;
          }
        })

      }
    })
  }
  export(content:any){
    this.modal.open(content, { centered: true, size: 'md', backdrop: 'static' })


  }
  download(){
    if(!(this.fromDate[0] && this.toDate[1])){
     this.toastr.warning('Select Dates')
     return
    }
    let fromDate = this.fromDate[0]
    let toData = this.toDate[1];
    this.http.post(ApiUrls.reconciliation,{
      start_date:Moment(new Date(fromDate)).format('YYYY-MM-DD'),
      end_date :Moment(new Date(toData)).format('YYYY-MM-DD'),
      // month:JSON.stringify(fromDate.getMonth()+1),//this.seletedMonth,
      // year :JSON.stringify(fromDate.getFullYear())//JSON.stringify(this.selectedyear)
    }).subscribe((res:any)=>{
      if(res.message.success){
        const link = document.createElement('a');
        link.setAttribute('target', '_blank');
        link.setAttribute('href', this.apiDomain+res.message.file_url);
        link.setAttribute('download', res.message.file_name);
        link.click();
        link.remove();
      }
    })
  }
}

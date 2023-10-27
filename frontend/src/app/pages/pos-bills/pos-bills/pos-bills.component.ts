import { HttpClient, HttpEventType } from '@angular/common/http';
import { Component, ElementRef, EventEmitter, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin, merge } from 'rxjs';
import { debounceTime, switchMap, takeUntil } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { DateToFilter } from 'src/app/shared/date-filter';
import { environment } from 'src/environments/environment';
import { WebTwain } from 'dwt/dist/types/WebTwain';
import { FiScannerService } from 'src/app/shared/services/fi-scanner.service';
import moment from 'moment';
import * as Moment from 'moment';
import { DateTimeAdapter } from 'ng-pick-datetime';
import { DatePipe } from '@angular/common'
import { FileuploadProgressbarService } from 'src/app/resuable/fileupload-progressbar/fileupload-progressbar.service';
import { SocketService } from 'src/app/shared/services/socket.service';
import print from 'print-js'
import { degrees, PDFDocument } from 'pdf-lib';




class posChecksFilter {
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
  search = '';
  checkNumber= '';
  checkDate= '';
  printed ='';
  sync = '';
  invoice_no = '';
  filterBy= 'Today';
  filterDate= '';
  filterType= 'creation'
  active= "1"
  pendingReview ='Pending Review'
}
@Component({
  selector: 'app-pos-bills',
  templateUrl: './pos-bills.component.html',
  styleUrls: ['./pos-bills.component.scss']
})
export class PosBillsComponent implements OnInit,OnDestroy {
  @ViewChild('scannedBillsForReview') scannedBillsForReview: ElementRef;
  @ViewChild('invoicePdf') invoicePdf: ElementRef;
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();

  filters = new posChecksFilter();
  onSearch = new EventEmitter();
  today = Moment(new Date()).format("YYYY-MM-DD")
  posCheckList = [];
  posCheckDetails: any = {};
  posBill: any = {};

  DWObject!: WebTwain;
  containerId = "dwtcontrolContainer";
  posChecksDate;
  fileTypes:any = [{document_type :'uuuuuu'},{document_type:"ooooooo"}]

  billDetails :any = {};
  active= "1"
  posChecks: any = {}
  name: any = {}
  check_no;
  table_number;
  // guest_name;
  lastSevenDays = moment(new Date()).subtract(7,'days').startOf('day').toDate();
  total_amount;
  attached_to:any;
  no_of_guests;
  creation;
  pos_bill;
  previewFile;
  apiDomain = environment.apiDomain;
  enteredInvNumber: string
  invoicesList: any = []
  posBillsData: any = {};
  erroMessage: any
  selectedInvoiceNo: any;
  isShown: boolean = false;
  dateOfreprocess
  relink:boolean = false;
  posItemName;
  companyDetails: any = {};
  posBillList:any=[];
  ngbDropdown: any
  latest_date: any
  selectedFiles = [];
  progressInfos =[];
  allFilesUplaoded;
  message;
  notSynced = false
  checkDate = ''
  date_type = ''
  public bWASM = false
  public dwtMounted = false
  scanningModule =false
  clbsModule: any;
  constructor(
    public modal: NgbModal,
    private router: Router,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private toaster: ToastrService,
    private scannerService : FiScannerService,
    public dateTimeAdapter: DateTimeAdapter<any>,
    public datepipe: DatePipe,
    public fileuploadProgressbarService : FileuploadProgressbarService,
    private socketService : SocketService
  )  {
    dateTimeAdapter.setLocale('en-IN');
  }
  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))

    if(this.companyDetails){
      this.filters.itemsPerPage = this.companyDetails.items_per_page;
      if(this.companyDetails?.company_code == 'ZBPK-01'){
        this.scanningModule = false
      }else{
        this.scanningModule = true
      }
      if(this.companyDetails.clbs == 1){
        this.clbsModule = true
      }else{
        this.clbsModule = false
      }
    }
    this.getPOSChecksData();
    this.getinvoicesList()

    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.posCheckList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });
    // this.dynamSoftOnload();
    // this.scannerService.dynamSoftOnload(false,this.containerId);
    this.scannerService.scannedFileUploadedRes.pipe(takeUntil(this.destroyEvents)).subscribe((res:any)=>{
      if(!res){return;}
      if(res.message){
        this.getPOSChecksData()
      }
    })

    merge(this.socketService.newPosChecks.pipe(takeUntil(this.destroyEvents)))
      .pipe(debounceTime(300)).subscribe((data) => this.getPOSChecksData());

    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res) {
        this.filters.checkDate =res.checkDate;
      }
    })
  }




  getPOSChecksData(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: posChecksFilter) => {
      // this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };

      if (this.filters.search) {
        queryParams.filters.push(['outlet', 'like', `%${this.filters.search}%`]);
      }
      if (this.filters.checkNumber) {
        queryParams.filters.push(['check_no', 'like', `%${this.filters.checkNumber}%`]);
      }
      if (this.filters.checkDate) {
        const today = Moment(this.filters.checkDate).format('YYYY-MM-DD');
        queryParams.filters.push(['check_date', '=', `${today}`])
      }

      if (this.filters.printed) {
        queryParams.filters.push(['printed', 'like', `%${this.filters.printed}%`]);
      }
      if (this.filters.sync) {
        queryParams.filters.push(['sync', 'like', `%${this.filters.sync}%`]);
      }
      if(this.filters.invoice_no){
        queryParams.filters.push(['attached_to','like',`%${this.filters.invoice_no}%`])
      }
      if(this.filters.pendingReview){
        queryParams.filters.push(['status','like',`%${this.filters.pendingReview}%`])
      }
      if (this.filters.filterBy) {

          if (this.filters.filterBy === 'Custom') {
            if (this.filters.filterDate) {
              const filter = new DateToFilter(Doctypes.posChecks, this.filters.filterBy, this.filters.filterDate as any, this.filters.filterType as any).filter;
              if (filter) {
                queryParams.filters.push(filter);
              }
            }
          } else if (this.filters.filterBy !== 'All') {
            const filter = new DateToFilter(Doctypes.posChecks, this.filters.filterBy, null, this.filters.filterType).filter;
            if (filter) {
              queryParams.filters.push(filter);
            }
          }

      }

      queryParams.limit_start = this.filters.start
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabPOS Checks`.`modified` desc"
      queryParams.fields = JSON.stringify(["*"]);
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.posChecks}`, {
        params: {
          fields: JSON.stringify(["count( `tabPOS Checks`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.posChecks}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.posCheckList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.posCheckList.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.start !== 0) {
          this.posCheckList = this.posCheckList.concat(data.data)
        } else {
          this.posCheckList = data.data;
        }
      }
    });
  }
  updateRouterParams(): void {
    this.router.navigate(['home/pos-bills'], {
      queryParams: this.filters
    });
  }
  viewPOSBill(showQr, item) {
    this.posBill['bill'] = item?.payload;
          let modal = this.modal.open(showQr, { size: 'md', centered: true });
    // if (item?.outlet) {
    //   this.http.get(`${ApiUrls.resource}/${Doctypes.outlets}/${item?.outlet}`).subscribe((res: any) => {
    //     if (res) {
    //       console.log(res);
    //       this.posBill['qrImg'] = environment.apiDomain + res?.data?.static_payment_qr_code;
    //       this.posBill['logo'] = environment.apiDomain + res?.data?.outlet_logo
    //       this.posBill['bill'] = item?.payload;
    //       let modal = this.modal.open(showQr, { size: 'md', centered: true });
    //     }
    //   })
    // }else{
    //   this.toaster.error("Check Outlet")
    // }

  }
  onDateFilterChange(){
    this.filters.currentPage = 1;
    if (this.filters.filterBy == 'Custom') {
      this.filters.filterDate = '';
    } else {
      this.updateRouterParams();
    }
  }
  checkPagination(): void {
    this.filters.currentPage = 1
    this.updateRouterParams()
  }
  printPOSBill(item) {

    if(this.companyDetails?.company_code == 'ZBPK-01'){
      this.http.get(`${ApiUrls.resource}/${Doctypes.posChecks}/${item.name}`).subscribe((res:any)=>{
        console.log(res)
        this.http.get(`${ApiUrls.resource}/${Doctypes.outlets}/${res?.data?.outlet}`).subscribe((result:any)=>{
           console.log(result)
           this.fileType('Tax Invoice',result?.data,res?.data).then((el:any)=>{
            if(res?.data){
              print({
                printable: el.split(',')[1],
                type: 'pdf',
                base64: true,
              });
            }else{
              this.toaster.error(res?.message?.message)
            }
           })

        });


      });
    }else{
    this.http.post(ApiUrls.posPrintBill, { data: { name: item.name } }).subscribe((res: any) => {
      if (res?.message?.success) {
        this.toaster.success(res?.message?.message)
      } else {
        this.toaster.error("Error")
      }
    })
    }


  }

  scanPosChecks(selectDateToScan,type){
    this.posChecksDate = '';this.date_type = type;
    if(type == 'scan'){
    this.scannerService.dynamSoftOnload(false,this.containerId)
    }
    let modal = this.modal.open(selectDateToScan,{ size: 'md', centered: true })
  }

  onChangeCategory(item,index){
    this.billDetails = item;
  }

  successCallback(){
    this.modal.open(this.scannedBillsForReview, {

    })
  }

  openInvoice(invoicePdf, name) {
    this.posItemName = name
    this.modal.open(invoicePdf, {
      size: 'lg',
      centered: true,
      windowClass: 'sideMenuPdf',
    });
    this.getPosChecks(name)

  }

  viewBillModel(viewBill) {
    this.modal.open(viewBill, {
      centered: true,
      size: 'md'
    });
    this.http.get(`${ApiUrls.getItemsForPosChecks}`, {
      params: {
        name:this.posItemName,
        // filters: JSON.stringify([["name", "=", `${this.posItemName}`]])
      }
    }).subscribe((res: any) => {
      this.posBillList = res.message.data;
      console.log(this.posBillList)
    })
  }


  getPosChecks(name){
    this.http.get(`${ApiUrls.resource}/${Doctypes.posChecks}/${name}`).subscribe((res: any) => {

      if (res.data) {
        // res.data.check_date=this.datepipe.transform(res.data.check_date, 'dd-MM-yyyy');
        this.posBillsData = res?.data;
        this.relink = ( res?.data?.sync == 'Yes') ? true : false;
        console.log("====================",this.relink)
        if( res?.data?.sync == 'Yes'){
        this.getLinkedInvoice(this.posBillsData?.attached_to)
        }
      }

    })
  }

  clearDate(){
    console.log("========", this.filters.checkDate)
    this.filters.checkDate = '';
    this.checkDate = ''
    this.updateRouterParams();
  }



  getLinkedInvoice(invoice_number){
    this.http.get(`${ApiUrls.resource}/${Doctypes.invoices}`, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify([['invoice_number','=',`${invoice_number}`]]),
        limit_page_length: 'None'
      }
    }).subscribe((res: any) => {
      // this.selectedInvoiceNo = res.data[0]
      this.relink = true;
    })
  }

  inputfocus() {
    this.enteredInvNumber = 'valid'
    const element: any = document.getElementsByClassName('paragraphClass');
    element[0].style.display = "block";
    const element2: any = document.getElementsByClassName('companyInputErrorMsg');
    element2[0].style.display = "none";
  }

  inputblur() {
    const element: any = document.getElementsByClassName('paragraphClass');
    const element2: any = document.getElementsByClassName('companyInputErrorMsg');
    setTimeout(() => {
      element[0].style.display = "none";
      element2[0].style.display = "block";
    }, 200);
  }

  companySearch(attached_to) {
    console.log("=========", attached_to)
    this.erroMessage =''
    this.http.get(`${ApiUrls.resource}/${Doctypes.invoices}`, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify([['invoice_number','like',`%${attached_to}%`]]),
        limit_page_length: 'None'
      }
    }).subscribe((res: any) => {
      console.log(res)
      if (res.data) {
        this.invoicesList = res?.data;
      }else{
        this.erroMessage = 'Invalid Invoice Number'
      }

    })
  }

  itemSelection(item) {
    console.log("===", item);
    this.posBillsData.attached_to = item.invoice_number;
    this.inputfocus();
    // this.gettaxPayerById(item1.name);
    this.selectedInvoiceNo = item
  }

  getinvoicesList() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.invoices}`, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify([]),
      }
    }).subscribe((res: any) => {
      // console.log(res)
      if (res.data) {
        this.invoicesList = res?.data;
      }

    })
  }


  closedCheck(check_type) {
    if(check_type == 'Check Closed'){
      return 'Closed Check';
    }else {
      return check_type
    }
  }

  invoiceLink(updateInvoicNo) {
    if (updateInvoicNo.form.invalid) {
      this.erroMessage = 'required'
      return
    }else {
      this.erroMessage = ''
    }
    this.http.put(`${ApiUrls.updateCheckInItems}`,{
      invoice_number:this.posBillsData.attached_to,
      check_name: this.posItemName

    }).subscribe((result: any) => {
      if(result.success){
        this.toaster.success("Updated");
      }else{
        this.toaster.warning(result.message.message);
      }
       this.getPosChecks(this.posBillsData?.name)
      this.posBillsData.attached_to = result?.data?.attached_to;
      this.getLinkedInvoice(this.posBillsData?.attached_to)
    })
  }


  updatePosBills(posForm:NgForm) {
    if(posForm.invalid){
      posForm.form.markAllAsTouched()
      return;
    }
    let data={
      check_no:this.posBillsData.check_no,
      creation:this.posBillsData.creation,
      table_number:this.posBillsData.table_number,
      total_amount:this.posBillsData.total_amount,
      no_of_guests:this.posBillsData.no_of_guests,
      check_date:this.posBillsData.check_date
    };
    // data.check_date=this.datepipe.transform(data.check_date, 'yyyy-MM-dd');

    this.http.put(`${ApiUrls.resource}/${Doctypes.posChecks}/${this.posBillsData?.name}`,data).subscribe((res: any) => {
      this.toaster.success("Updated");

    })



  }

  uploadPosChecksFn(uploadPOSChecks){
    this.message = ''; this.selectedFiles=[];this.progressInfos=[];this.allFilesUplaoded=false
    let modal = this.modal.open(uploadPOSChecks,{size:'lg',centered:true})
    modal.result.then((res:any) => {
      if(res=='success'){
        this.getPOSChecksData();
      }
    })
  }

  selectFiles(files) {
    Array.from(files).forEach(file => {
      this.selectedFiles.push({ progress: 0, file });
    });
  }

  removeFromList(file, i) {
    this.selectedFiles.splice(i, 1)
  }

  async uploadFiles() {
    let data ={
      files : this.selectedFiles,
      is_private : 1,
      folder:'Home',
      attached_to_doctype:Doctypes.posChecks,
      date: this.posChecksDate,
      attached_to_name:'POS Checks'
    }
    this.fileuploadProgressbarService.isFilesUploading.emit(true)
    setTimeout(() => {
    this.fileuploadProgressbarService.uploadedFiles.emit(data)

    }, 500);
    this.message = '';
    this.modal.dismissAll()

  }


  onTabChange(e){
    this.active = e.nextId;
    if(this.active == "2"){
      this.filters.pendingReview = "Reviewed"
    }else{
      this.filters.pendingReview = "Pending Review"
    }
    this.updateRouterParams()

  }

  checkedItemsAll(e){
    if(this.notSynced){
      this.filters.sync = "No"
    }else{
      this.filters.sync = ""
    }
    this.updateRouterParams();
  }

  /** Update Reviewed */
  finishReview(modal:NgbModal){
    this.http.put(`${ApiUrls.resource}/${Doctypes.posChecks}/${this.posBillsData.name}`,{
      status:'Reviewed'
    }).subscribe((res:any)=>{
      if(res){
        this.toaster.success("Reviewed")
        this.getPOSChecksData()

      }
    })
  }
  /********* */

  selectCheckDate(){
    // console.log(e)
    this.filters.checkDate =this.checkDate;
    this.updateRouterParams()
  }

  async fileType(title: string,outletData:any,poscheckData:any) {
    let qrPng =outletData?.static_payment_qr_code;

    let xyz = this.apiDomain + poscheckData?.pos_bill;
    const existingPdfBytes = await fetch(xyz).then(res => res.arrayBuffer())
    const pdfDoc = await PDFDocument.load(existingPdfBytes, { ignoreEncryption: true });
    pdfDoc.setTitle(title);

    const pages = pdfDoc.getPages();
    const firstPage = pages[0];
    let sampleImg = qrPng ? this.apiDomain + qrPng : null;
    if (sampleImg) {
      const imgBytes = await this.http.get(sampleImg, { responseType: 'arraybuffer' }).toPromise();
      const pngImage = await pdfDoc.embedPng(imgBytes);

      const pngDims = pngImage.scale(0.6);

      firstPage.drawImage(pngImage, {
        x: 290 ,//parseInt(this.companyDetails.qr_rect_x0),
        y: 670,
        width: 110,
        height: 110
      });
      const pdfDataUri = await pdfDoc.saveAsBase64({ dataUri: true, addDefaultPage: true });
      this.previewFile = pdfDataUri;

      // console.log("Preview File", this.previewFile)
      return await this.previewFile;
    } else {
      this.toaster.error('QR img not found')
      // console.log('QR img not found');

    }
  }
  ngOnDestroy(){
    this.modal.dismissAll();
    this.destroyEvents.next();
    this.destroyEvents.unsubscribe();
  }



}

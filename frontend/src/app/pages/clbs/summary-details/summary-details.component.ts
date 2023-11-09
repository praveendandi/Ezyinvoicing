import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, EventEmitter, OnInit, ViewChild } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal, NgbNavChangeEvent } from '@ng-bootstrap/ng-bootstrap';
import moment from 'moment';
import { ToastrService } from 'ngx-toastr';
import { map, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { DateToFilter } from 'src/app/shared/date-filter';
import { environment } from 'src/environments/environment';
import { PDFDocument } from 'pdf-lib';
import { SocketService } from 'src/app/shared/services/socket.service';
import { DateTimeAdapter } from 'ng-pick-datetime';

@Component({
  selector: 'app-summary-details',
  templateUrl: './summary-details.component.html',
  styleUrls: ['./summary-details.component.scss'],
})
export class SummaryDetailsComponent implements OnInit {
  @ViewChild('addSignature') addSignature : ElementRef;
  @ViewChild('preview') preview : ElementRef;
  @ViewChild('widgetsContent') widgetsContent: ElementRef;
  onChangeParticulars: any = new EventEmitter()

  active = 1;
  data = new Array(20)
  paramsID: any
  summaryData: any = {};
  summaryInfo: any = {};
  invoicesData: any = {};
  invoicesTabs: any = [];
  paymentsList: any = [];
  paymentData: any = {};
  company: any = {};
  totalAmt: any = '';
  refundAmt: any = '';
  selectedInvoicesList: any = [];
  itemChangesToSave: any = [];
  printFormats: any;
  categoryData: any = {}
  contactsByLocation: any = [];
  contacts: any = [];
  printEnable = false;
  selectedCategoryDetails: any = {}
  filePdf = ''
  apiDomain = environment.apiDomain
  emailTempData: any = {}
  activityLogs = [];
  dispatchInfo: any = {}
  minDispatchDate: any;
  saveSummaryPO = false;
  previewFile;
  previewFileSize;
  clbsSettings:any = {};
  emailLogs: any;
  loginData: any;
  userSignatureDetails: any;


  constructor(
    private http: HttpClient,
    private router: Router,
    public socketService : SocketService,
    private activatedRoute: ActivatedRoute,
    public dateTimeAdapter: DateTimeAdapter<any>,
    private modal: NgbModal,
    private toastr: ToastrService
  ) {
    dateTimeAdapter.setLocale('en-IN');
   }

  ngOnInit(): void {
    this.contacts = [];
    this.loginData = JSON.parse(localStorage.getItem('login'))
    this.company = JSON.parse(localStorage.getItem('company'));

    this.activatedRoute.params.subscribe((res: any) => this.paramsID = res?.id)
    this.getSummaryDetails();
    this.getCompanyDetails()
    this.getClbsSettings();

  }

  getCompanyDetails() {
    this.http.get(`${ApiUrls.company}/${this.company?.name}`).subscribe((res: any) => {
      if (res) {
        this.company = res.data;
      }
    })
  }
  getUserSignature(){
    let user:any = JSON.parse(localStorage.getItem('login'))
    console.log(user)
    this.http.get(`${ApiUrls.resource}/${Doctypes.userSignature}`, {
      params:{
        filters:JSON.stringify([['name','=',user?.email]]),
        fields:JSON.stringify(['*'])
      }
    }).subscribe((res: any) => {
      if(res?.data){
        this.userSignatureDetails = res.data[0]
        console.log(this.userSignatureDetails)
      }
    })
  }

  getSummaryDetails(check = true) {

    this.http.get(`${ApiUrls.resource}/${Doctypes.summaries}/${this.paramsID}`).subscribe((res: any) => {
      if (res) {
        this.summaryData = res.data;
        let modified_date =  new Date(this.summaryData.modified)
        this.minDispatchDate = new Date(modified_date.getFullYear(), modified_date.getMonth(),modified_date.getDate())
        if (check) {
          this.getSummariedData();
        }
        this.getInvoicesfilteredData(this.summaryData)
        this.getContactByLoctaion();
        this.getUserSignature()
        // this.getActivityLogs();
      }
    })
  }
  getSummariedData() {
    this.http.get(`${ApiUrls.getBreakup}`, {
      params: {
        summary: this.paramsID
      }
    }).subscribe((res: any) => {
      if (res?.message?.success) {
        this.invoicesData = res?.message;
        this.totalAmt = this.invoicesData?.data?.map((each: any) => each.amount).reduce((prev, curr) => prev + curr, 0);
        this.invoicesTabs = this.invoicesData?.breakup_details_data
        this.getPaymentsList()
        this.checkWidthOfTabsScrollBar()
      } else {
        this.invoicesData = {};
        this.active = 1;
      }
    })
  }
  getInvoicesfilteredData(obj) {
    if (!obj) { return }
    const queryParams: any = { filters: [] };
    if (this.paramsID) {
      queryParams.filters.push(['summary', '=', `${this.paramsID}`]);
    }
    // if (obj?.tax_payer_details) {
    //   queryParams.filters.push(['gst_number', 'like', `%${obj?.tax_payer_details}%`]);
    // }
    if (obj.from_date) {
      const filter = new DateToFilter('Invoices', 'Custom', [obj.from_date, obj.to_date] as any, 'invoice_date' as any).filter;
      if (filter) {
        queryParams.filters.push(filter);
      }
    }
    queryParams.limit_page_length = 'None';
    queryParams.fields = JSON.stringify(['*'])
    queryParams.filters = JSON.stringify(queryParams.filters);
    queryParams.order_by = "`tabInvoices`.`invoice_date` desc";
    this.http.get(`${ApiUrls.resource}/${Doctypes.invoices}`, { params: queryParams }).subscribe((res: any) => {
      if (res?.data) {
        this.selectedInvoicesList = res.data;
      }
    })
  }



  addInvoices(pageType) {
    this.router.navigate(['./clbs/invoices/' + this.paramsID,{type:pageType}])
  }
  goBack() {
    this.router.navigate(['./clbs/summaries'])
  }
  getPaymentsList() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.summaryPayments}`, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify([['summary', 'like', `${this.paramsID}`]]),
        limit_page_length: 'None'
      }
    }).subscribe((res: any) => {
      if (res?.data) {
        this.paymentsList = res?.data;
        let payAmt = this.paymentsList.map((each: any) => each.amount).reduce((prev, curr) => prev + curr, 0);
        this.refundAmt = this.totalAmt - payAmt
      }
    })
  }

  addPayments(addPayment) {
    this.paymentData = {};
    let modal = this.modal.open(addPayment, { centered: true, size: 'md' })

  }
  createSummary(form: NgForm, modal) {
    if (form.invalid) {
      form.form.markAllAsTouched();
      return;
    }
    form.value['doctype'] = Doctypes.summaryPayments;
    form.value['summary'] = this.paramsID;
    form.value['company'] = this.company.name;

    const formData = new FormData();
    formData.append('doc', JSON.stringify(form.value));
    formData.append('action', 'Save');
    this.http.post(`${ApiUrls.fileSave}`, formData).subscribe((res: any) => {
      if (res) {
        this.toastr.success('New Payment Added')
        modal.close(res)
        this.getPaymentsList();
        this.getSummaryDetails()
      }
      // this.router.navigate(['./clbs/summary-details/'+res?.docs[0]?.name])
    })
  }
  cancelAddPayment(){
    this.getPaymentsList()
  }
  previewDoc(documentWith) {
    if(!this.invoicesData?.data?.length){
      this.toastr.warning('no data found in summary breakups')
      return
    }
    this.getPrintFormtsById(documentWith)
    // this.modal.open(preview, { size: 'lg', centered: true, windowClass: 'sideMenuPdf' })
  }
  verifyPFX_password(verifyPfx_password){
    if(!this.invoicesData?.data?.length){
      this.toastr.warning('no data found in summary breakups')
      return
    }
    this.modal.open(verifyPfx_password, { size: 'md', centered: true })
  }
  submitTheVerifyPassword(documentWith,form:NgForm){
    this.http.get(`${ApiUrls.resource}/${Doctypes.userSignature}`, {
      params:{
        filters:JSON.stringify([['name','=',this.loginData?.name]]),
        fields:JSON.stringify(['*'])
      }
    }).subscribe((res: any) => {
      if(res.data){
        if(res?.data[0]?.pfx_password == form.form.value.password){
          this.submitSummary(documentWith)

        }else{
          this.toastr.error('Invalid Password')
        }
      }else{
        this.toastr.error(res?.message?.message)
      }
    })
  }
  getPrintFormtsById(documentWith) {

    this.printFormats = []
    let data:any

    if(documentWith == 'noSignature'){
      data = {
        name: this.paramsID
      }
    }else if(documentWith == 'addSignature'){
      let selectedContact = JSON.parse(this.summaryData?.contacts);
      if (!selectedContact.length) {
        this.toastr.info('Please Select Contact.')
        return
      }
      data = {
        name: this.paramsID ,
        add_signature:true
      }
    }

    this.http.get(`${ApiUrls.summaryPdfFiles}`, { params: data }).subscribe((res: any) => {
      console.log(res)
      if (res?.message?.success) {
        let modalRef = this.modal.open(documentWith == 'addSignature'?this.addSignature:this.preview, { size: 'lg', centered: true, windowClass: 'printModal',backdrop:'static' })
        modalRef.result.then((res: any) => {
          if(documentWith == 'addSignature'){
            window.location.reload()
          }
        })
        this.previewFileSize = res?.message;
        this.printFormats = res?.message?.files?.map((each: any) => {
          if (each) {
            let arr = Object.entries(each);
            let obj = {}
            obj['key'] = arr[0][0]; obj['val'] = this.apiDomain + arr[0][1]
            return obj;
          }
        })
        if (this.printFormats.length) {
          this.categoryData.category = this.printFormats[0]?.val
          this.filePdf = this.printFormats[0]?.val
        }

      } else {
        this.toastr.error('Failed to Load')
      }
    })

  }
  test(values) {
    console.log(values.currentTarget.checked)
  }
  selectPrint(e) {
    this.filePdf = this.categoryData.category
    // document.getElementById('printFormats').innerHTML = this.categoryData.category
  }
  deleteInvoicesfrmSummary(item) {
    this.http.get(`${ApiUrls.deleteInvoiceFrmSmry}`, {
      params: {
        summary: this.paramsID,
        deleted_invoices: JSON.stringify([item.name])
      }
    }).subscribe((res: any) => {
      if (res?.message?.success) {
        this.toastr.info('Deleted')
        this.getInvoicesfilteredData(this.summaryData);
        this.getSummaryDetails();
      }
    })
  }

  onNavChange(changeEvent: NgbNavChangeEvent) {
    this.selectedCategoryDetails = {}
    //  this.getInvoicesfilteredData(this.summaryData);
    //  this.getPaymentsList()
    //  this.getSummaryDetails();
  }


  onChangeByCtgry(e, item, type) {
    let obj = {};
    if (type == 'particulars') {
      obj['particulars'] = e.target.value;
    }
    if (type == 'bill_no') {
      obj['bill_no'] = e.target.value;
    }
    obj['name'] = item?.name
    this.itemChangesToSave.push(obj)
    const unique = [];
    this.itemChangesToSave.reverse().map(x => unique.filter(a => a.name == x.name).length > 0 ? null : unique.push(x));
    this.itemChangesToSave = unique;
  }

  saveChangesFun() {
    if (this.itemChangesToSave.length) {
      this.http.post(ApiUrls.updateSummary, {
        data: {
          summary: this.itemChangesToSave
        }
      }).subscribe((res: any) => {
        if (res?.message?.success) {
          this.itemChangesToSave = [];
          // this.getSummariedData();
        } else {
          this.toastr.error("Error")
        }
      })
    } else {
      this.toastr.info("No Changes to Save")
    }
  }
  addContact(addContact) {
    this.getContactByLoctaion();
    let modalVal = this.modal.open(addContact, { size: 'md', centered: true, windowClass: 'sideMenu' })
    modalVal.result.then((res: any) => {
      this.getContactByLoctaion();
    })

  }
  newContact(){
    this.socketService.isContactAdded.subscribe((res:any)=>{
      // this.getSummaryDetails()
      console.log(res)
      if(res == 'refresh'){
        window.location.reload()
      }
    })
  }
  getContactByLoctaion() {
    this.contacts = [];
    this.http.get(`${ApiUrls.contacts}`, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify([['location', '=', this.summaryData?.location], ['contact_status', '=', 1]]),
        limit_page_length: 'None'
      }
    }).subscribe((res: any) => {
      if (res?.data) {
        this.contactsByLocation = res?.data.map((each: any, index) => {
          JSON.parse(this.summaryData?.contacts).forEach(element => {
            if (element && element == each.name) {
              each.summaryStatus = true;
            }

          });
          return each;
        })
        console.log(this.contactsByLocation)
        if (this.contactsByLocation?.length) {
          this.contacts = this.contactsByLocation.filter((each: any) => {
            if (each?.contact_status === 1 && each.summaryStatus) {
              return each;
            }
          })
          this.contacts = this.contacts.slice(0, 2);
        }

      }
    })
  }
  addContactToSummary(item, type) {
    let selectedContact = JSON.parse(this.summaryData?.contacts)
    if (type == 'add') {
      selectedContact.push(item.name)
    }
    if (type == 'remove') {
      const index = selectedContact.indexOf(item?.name);
      if (index > -1) {
        selectedContact.splice(index, 1);
      }
    }
    this.http.put(`${ApiUrls.resource}/${Doctypes.summaries}/${this.paramsID}`, { contacts: JSON.stringify(selectedContact) }).subscribe((res: any) => {
      this.getSummaryDetails(false);
      // if (res) {
      //   let selectedContact = JSON.parse(this.summaryData?.contacts)
      //   console.log("==== type == ",type,"========",this.summaryData?.contacts)
      //   if (type == 'add') {
      //     selectedContact.push(item.name)
      //   }
      //   if (type == 'remove') {
      //     const index = selectedContact.indexOf(item?.name);
      //     if (index > -1) {
      //       selectedContact.splice(index, 1);
      //     }
      //   }
      // }
    })
  }

  downloadAllFiles() {

    var temporaryDownloadLink = document.createElement("a");
    temporaryDownloadLink.style.display = 'none';
    document.body.appendChild(temporaryDownloadLink);

    for (var n = 0; n < this.printFormats.length; n++) {
      var download = this.printFormats[n];
      temporaryDownloadLink.setAttribute('href', download.val);
      temporaryDownloadLink.setAttribute('download', download.key);
      temporaryDownloadLink.click();
    }

    document.body.removeChild(temporaryDownloadLink);
  }

  seletedCatgry(item) {
    this.selectedCategoryDetails = item
  }

  submitSummary(documentWith=null) {
    let selectedContact = JSON.parse(this.summaryData?.contacts);
    if (!selectedContact.length) {
      this.toastr.info('Please Select Contact.')
    } else {

      this.http.get(`${ApiUrls.submitSummary}`, { params: { summary: this.paramsID } }).subscribe((res: any) => {
        if (res?.message?.success) {
          this.active = 1;
          this.getSummaryDetails();

          // this.toastr.success("Submitted")
          this.toastr.success(res?.message?.message)
          if(documentWith == 'addSignature'){
            this.previewDoc(documentWith)
          }

        } else {
          this.toastr.error(res?.message?.message)
        }
      })
    }
  }

  getClbsSettings() {
    this.http.get(`${ApiUrls.clbsSettings}`).subscribe((res: any) => {
      if (res?.data[0]) {
        this.http.get(`${ApiUrls.clbsSettings}/${res?.data[0]?.name}`,{
          params: {
            fields: JSON.stringify(['*']),
          }
        }).subscribe((each: any) => {
          if (each) {
            this.clbsSettings = each?.data;
          }
        })
      }
    })
  }

  sendEmailTemp(sendEmail) {
    this.emailTempData.recipients = this.contacts.map((each: any) => each.email_id)
    let modal = this.modal.open(sendEmail, { size: 'lg', centered: true ,windowClass:'sideMenu50'})
    // this.getDocumentsList()
    this.getClbsSettings();
  }
  emailForm(form: NgForm, modal) {
    if (form.valid) {

      this.http.put(`${ApiUrls.clbsSettings}/${this.company?.name}`, { data: { cc_mail_ids_for_clbs_reports: form.value.cc_mail_ids_for_clbs_reports } }).subscribe((res: any) => {
        if (res) {
          let dataObj = {
            summary: this.paramsID,
            subject: form.value.subject,
            email: form.value.recipients,
            response: form.value.message
          }
          this.http.post(`${ApiUrls.sendEmailSummary}`, { data: dataObj }).subscribe((res: any) => {
            if (res?.message?.success) {
              this.toastr.success("Email Sent")
              modal.close('success');
            } else {
              this.toastr.error("Error")
            }
          })
          this.getCompanyDetails()
        }
      })
    } else {
      form.form.markAllAsTouched();
      this.toastr.error("Error")
    }
  }

  getDispatchDetails(temp) {
    const queryParams = {
      filters: JSON.stringify([['summaries', '=', this.paramsID]]),
      fields: JSON.stringify(['*'])
    }
    this.http.get(`${ApiUrls.resource}/${Doctypes.dispatchInfo}`, { params: queryParams }).subscribe((res: any) => {
      if (res?.data.length) {
        this.dispatchInfo = res?.data[0];
        // this.dispatchInfo['dispatch_date'] = moment(this.dispatchInfo.dispatch_date).format("DD/MM/YYYY");
        // console.log(this.dispatchInfo)
        let modal = this.modal.open(temp, { size: 'md', centered: true ,windowClass:'sideMenu30'})
      } else {
        this.dispatchInfo = {}
        let modal = this.modal.open(temp, { size: 'md', centered: true,windowClass:'sideMenu30' })
      }
    })
  }

  dispatchTempFunc(temp) {
    this.getDispatchDetails(temp);
  }
  dispatchFormAdd(form, modal) {
    if (form.form.valid) {
      let formValue = form.value;
      formValue['dispatch_date'] = moment(form.value.dispatch_date).format("YYYY/MM/DD");
      let data = {
        ...formValue, summaries: this.paramsID
      }
      this.http.post(`${ApiUrls.resource}/${Doctypes.dispatchInfo}`, { data: data }).subscribe((res: any) => {
        if (res) {
          this.toastr.success("Success")
          modal.close('success');
          this.active = 1;
          this.getSummaryDetails()
        }
      })
    }
  }
  dispatchFormEdit(form, modal) {
    let data = {
      ...form.value, summaries: this.paramsID
    }
    this.http.put(`${ApiUrls.resource}/${Doctypes.dispatchInfo}/${this.dispatchInfo?.name}`, { data: data }).subscribe((res: any) => {
      if (res) {
        this.toastr.success("Success")
        modal.close('success');
        this.getSummaryDetails()
      }
    })
  }
  activityOpen(activityLog) {
    this.getActivityLogs()
    let modalVal = this.modal.open(activityLog, { size: 'md', centered: true, windowClass: 'sideMenu' })
  }
  emailLogOpen(emailLog) {
    this.getEmailLogs()
    let modalVal = this.modal.open(emailLog, { size: 'md', centered: true, windowClass: 'sideMenu' })
  }

  getEmailLogs() {
    let params = {
      summary:this.paramsID,
      // filters: JSON.stringify([['docname', '=', `${this.paramsID}`]]),
      // limit_page_length: "None",
      fields: JSON.stringify(['*'])
    }
    this.http.get(`${ApiUrls.email_tracking}`, { params: params }).subscribe((res: any) => {
      if (res?.data) {
        let items = res?.data.map((each: any) => {
          if (each.emails) {
            each.emails = JSON.parse(each.emails)
          }
          return each
        })
        this.emailLogs = items;
        console.log(this.emailLogs)

      }
    })

  }
  getActivityLogs() {
    let params = {
      filters: JSON.stringify([['docname', '=', `${this.paramsID}`]]),
      // limit_page_length: "None",
      // fields: JSON.stringify(['*'])
    }
    this.http.get(`${ApiUrls.summary_activity_log}`, { params: { summary: this.paramsID } }).subscribe((res: any) => {
      if (res?.message?.success) {
        let items = res?.message?.data.map((each: any) => {
          if (each.data) {
            each.data = JSON.parse(each.data)
          }
          return each
        })
        this.activityLogs = items;
        console.log(this.activityLogs)

      }
    })
    // this.http.get(`${ApiUrls.summaryActivityLog}`, { params: params }).subscribe((res: any) => {
    //   if (res?.success) {
    //     let items = res?.data.map((each: any) => {
    //       if (each.data) {
    //         each.data = JSON.parse(each.data)
    //       }
    //       return each
    //     })
    //     this.activityLogs = items;
    //     console.log(this.activityLogs)

    //   }
    // })

    // this.http.get(`${ApiUrls.summaryActivityLog}/${this.paramsID}`).subscribe((res:any)=>{
    //   console.log(res)
    // })
    // this.http.get(ApiUrls.resource + `/DocType/` + Doctypes.summaries).pipe(switchMap((res: any) => {
    //   return this.http.get(ApiUrls.resource + '/Version', {
    //     params: {
    //       filters: [JSON.stringify([['docname', '=', this.paramsID]])],
    //       fields: JSON.stringify(['data', 'name', 'creation', 'modified_by']),
    //       order_by: `${'creation desc'}`,
    //     }
    //   }).pipe(map((response: any) => {
    //     res.data.dataFields = res.data.fields.reduce((prev, nxt) => {
    //       prev[nxt.fieldname] = nxt.label;
    //       return prev;
    //     }, {});
    //     return (response.data as any[]).map((each) => {
    //       each.data = JSON.parse(each.data);
    //       each.data = Object.keys(each.data).reduce((prev, key) => {
    //         if (each.data[key] && Array.isArray(each.data[key]) && each.data[key].length) {
    //           prev[key] = each.data[key].map((cr: string[]) => {
    //             if (cr.length == 3) {
    //               cr[0] = res.data.dataFields[cr[0]] || cr[0];
    //             }
    //             return cr;
    //           });
    //         } else {
    //           prev[key] = each.data[key];
    //         }
    //         return prev;
    //       }, {});
    //       return each;
    //     });
    //   }))
    // })).subscribe((res) => {
    //   this.activityLogs = res;
    //   console.log(res)
    // });
  }

  paymentItem(addPayment, item, type) {
    this.paymentData = item;
    if (type == 'edit') {
      let modal = this.modal.open(addPayment, { centered: true, size: 'md' })
    }
    if (type == 'Deleted') {
      if (!window.confirm(`Are you sure to delete payment ${item.payment_description} ?`)) {
        return null;
      } else {
        this.http.delete(`${ApiUrls.resource}/${Doctypes.summaryPayments}/${this.paymentData?.name}`).subscribe((res: any) => {

          if (res) {
            this.getPaymentsList();
          }
        })
      }
    }

  }

  editPayment(form, modal) {
    if (form.valid) {
      this.http.put(`${ApiUrls.resource}/${Doctypes.summaryPayments}/${this.paymentData?.name}`, { data: form.value }).subscribe((res: any) => {
        if (res) {
          modal.close();
          this.getPaymentsList();
          this.getSummaryDetails()
        }
      })
    } else {
      form.form.markAllAsTouched();
      return;
    }
  }

  poNumberFunc(e) {
    if (e) {
      this.saveSummaryPO = true;
    }
  }
  savePOFunc() {
    this.http.put(`${ApiUrls.resource}/${Doctypes.summaries}/${this.paramsID}`, { data: { po_number: this.summaryData.po_number } }).subscribe((res: any) => {
      this.saveSummaryPO = false;
      this.getSummaryDetails()
    })
  }

  async getDocumentsList() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.summaryDocuments}`, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify([['summary', '=', this.paramsID], ['document_type', '=', 'Invoices']]),
        limit_page_length: 'None'
      }
    }).subscribe((res: any) => {
      if (res?.data) {
        // console.log("====== data ==== ", res?.data)

        res?.data.map(async (each: any) => {
          if (each?.document && each?.qr_code_image) {

            const formData = new FormData();
            const fileAsArray: any = await this.fileType(each, true);
            console.log("file ======",fileAsArray)
            const blob = this.dataURLtoFile(fileAsArray,Date.now() + 'with-qr.pdf');
            // const url = URL.createObjectURL(blob);

            // window.open(url,'_blank');
            // formData.append('file', new Blob([fileAsArray], { type: "application/pdf" }), Date.now() + 'with-qr.pdf');

            formData.append('file',blob);
            formData.append('is_private', '1');
            formData.append('folder', 'Home');
            formData.append('doctype', Doctypes.summaryDocuments);
            formData.append('fieldname', 'invoice');
            formData.append('docname', each.name);
            this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
              if (res) {
                console.log("res ===== ",res)
              }
            })

          }

        })


      }
    })
  }


  async fileType(each, returnFile = false) {
    // console.log("===============")
    let qrPng;
    let invoiceTitle = 'Tax Invoice';
    qrPng = each?.qr_code_image;
    let xyz = this.apiDomain + each?.document;
    const existingPdfBytes = await fetch(xyz).then(res => res.arrayBuffer())
    const pdfDoc = await PDFDocument.load(existingPdfBytes, { ignoreEncryption: true });
    pdfDoc.setTitle(invoiceTitle);

    const pages = pdfDoc.getPages();
    const firstPage = this.company?.qr_page == 'Last' ? pages[pages.length - 1] : pages[0];
    let sampleImg = qrPng ? this.apiDomain + qrPng : null;
    if (sampleImg) {
      const imgBytes = await this.http.get(sampleImg, { responseType: 'arraybuffer' }).toPromise();
      const pngImage = await pdfDoc.embedPng(imgBytes);
      const pngDims = pngImage.scale(0.6);
      firstPage.drawImage(pngImage, {
        x: parseInt(this.company.qr_rect_x0),
        y: firstPage.getHeight() - parseInt(this.company.qr_rect_y0) - parseInt(this.company.qr_rect_y1),
        width: parseInt(this.company.qr_rect_x1),
        height: parseInt(this.company.qr_rect_y1)
      });
      const pdfDataUri = await pdfDoc.saveAsBase64({ dataUri: true, addDefaultPage: true });
      this.previewFile = pdfDataUri;

      // if (returnFile) {
      //   return await pdfDoc.save();
      // }

      return this.previewFile;
    } else {
      console.log('QR img not found');

    }
  }


  dataURLtoFile(dataurl, filename) {

    var arr = dataurl.split(','),
        mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]),
        n = bstr.length,
        u8arr = new Uint8Array(n);

    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }

    return new File([u8arr], filename, {type:mime});
}
checking(event){
	var data = event.target.value;
	if((event.charCode>= 48 && event.charCode <= 57) || event.charCode== 46 ||event.charCode == 0){
		if(data.indexOf('.') > -1){
 			if(event.charCode== 46)
  				event.preventDefault();
		}
	}else
		event.preventDefault();
	};


  addSignatureToPreview(addSignature){
    this.printFormats = []
    let data:any ={
      name: this.paramsID ,
      add_signature:true
    }
    this.http.get(`${ApiUrls.summaryPdfFiles}`, { params: data }).subscribe((res: any) => {
      console.log(res)
      if (res?.message?.success) {
        this.modal.open(addSignature, { size: 'lg', centered: true, windowClass: 'printModal' })
        this.previewFileSize = res?.message;
        this.printFormats = res?.message?.files?.map((each: any) => {
          if (each) {
            let arr = Object.entries(each);
            let obj = {}
            obj['key'] = arr[0][0]; obj['val'] = this.apiDomain + arr[0][1]
            return obj;
          }
        })
        if (this.printFormats.length) {
          this.categoryData.category = this.printFormats[0]?.val
          this.filePdf = this.printFormats[0]?.val
        }

      } else {
        this.toastr.error('Failed to Load')
      }
    })
  }
  amendTheSummary(amendSummary){
    this.modal.open(amendSummary,{size:'lg',centered:true})
  }
  submitAmendSummary(form:NgForm){
    if(form.invalid){
      return
    }
    let data={
      summary:this.paramsID,
      reason_for_amendment:form.form.value.reason_for_amendment
    }
    this.http.put(`${ApiUrls.summary_amendment}`, data).subscribe((res: any) => {
       this.modal.dismissAll()
       this.router.navigate(['./clbs/summaries'])
      //  this.router.navigate(['./clbs/summary-details/'+res?.message?.summary])
      //   setTimeout(()=>{
      //     window.location.reload()
      //   },200)

    })
  }
  scrollLeft() {
    this.widgetsContent.nativeElement.scrollLeft -= 150;
  }

  scrollRight() {
    this.widgetsContent.nativeElement.scrollLeft += 150;
  }

  ngbNavLinkClick(navlink){
    console.log(navlink)
  }
  checkWidthOfTabsScrollBar(){
    setTimeout(() => {
      document.onreadystatechange = function () {
        if (document.readyState == "complete") {
        var pixels = document.getElementById("scroll-l").offsetWidth ;
        var screenWidth = window.screen.width;
        var percentage = (pixels / screenWidth ) * 100; // 0.92%
        console.log(percentage)
        if(percentage>38){
          return true
        }else{
          return false
        }
      }
    }
    }, 1000);


  }

}

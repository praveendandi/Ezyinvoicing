import { degrees, PDFDocument } from 'pdf-lib';
import { switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from './../../../shared/api-urls';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, OnDestroy, OnInit, resolveForwardRef, ViewChild } from '@angular/core';
import { NgbActiveModal, NgbModal, NgbNavConfig } from '@ng-bootstrap/ng-bootstrap';
import { NgForm } from '@angular/forms';
import { environment } from 'src/environments/environment';
import { UserService } from 'src/app/shared/services/user.service';
import { DomSanitizer } from '@angular/platform-browser';
import { ToastrService } from 'ngx-toastr';
import * as Moment from 'moment';
import { stateCode } from 'src/app/shared/state-codes';
import { SacHsnComponent } from 'src/app/shared/models/sac-hsn/sac-hsn.component';
import { TempSacLineComponent } from 'src/app/shared/models/temp-sac-line/temp-sac-line.component';
import { ActivitylogComponent } from '../../activitylog/activitylog.component';
import print from 'print-js'
import { SplitLineItemsComponent } from 'src/app/shared/models/split-line-items/split-line-items.component';
import { UOMCode } from 'src/app/shared/uom-codes';
import { Location } from '@angular/common';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';
import * as html2pdf from 'html2pdf.js';

@Component({
  selector: 'app-invoice-details',
  templateUrl: './invoice-details.component.html',
  styleUrls: ['./invoice-details.component.scss'],
  providers: [NgbNavConfig]
})
export class InvoiceDetailsComponent implements OnInit, OnDestroy {
  @ViewChild('menu') menu: ElementRef;
  @ViewChild('uploadModal') uploadModal: ElementRef;
  @ViewChild('emailTemp') emailTemp: ElementRef;
  @ViewChild('B2CtoB2CTemp') B2CtoB2CTemp: ElementRef;
  @ViewChild('invoicePdf') invoicePdf: ElementRef;
  @ViewChild('invoiceDateEdit') invoiceDateRef: ElementRef;
  @ViewChild('addInvoiceModal') addInvoiceModal: ElementRef;
  @ViewChild('pmsPDF') pmsPDF: ElementRef;
  @ViewChild('sezGenerateIRN') sezGenerateIRN: ElementRef;
  @ViewChild('lutExempted') lutExempted: ElementRef

  private total = 0;
  private value;

  lut_exempted;
  invoicetypeName;
  invoicetype = true;
  invoiceInfo: any = {};
  invoiceTitle;
  editData;
  active = 1;
  activityLogs = [];
  activityLog;
  params;
  isCopy = false;
  TaxInvoice = false;
  CreditInvoice = false
  apiDomain = environment.apiDomain;
  fileToUpload: File;
  imgURL;
  filename;
  sortedListInvoice = [];
  pdfListItems = [];
  creditSummarySorted = [];
  errorMessage;
  successMessage;
  pdfView = true;
  emailTempData: any = {};
  templatesList = []
  fileName = [];
  checkName = false;
  taxPayerDetails: any = {};
  checkApiMethod = false;
  apiMethod;
  companyDetails;
  navNumber;
  emailData;
  previewFile;
  customInvoiceType = false;
  myDate = new Date();
  stateCode: any;
  sez = false;
  lut = false;
  invoiceNumber;
  isChecked = false;
  dupItems: any = []
  dupArrayList = [];
  stateCodes;
  place_of_supply;
  place_of_supply_state;
  editPOD = true;
  loginData;
  checkSplit = false;
  today = Moment(new Date()).endOf('day').toDate();
  maxItemDate;
  creditInvoiceItem: any = {
    net: 'No'
  };
  sacDetails;
  uomData;
  sacCodeName;
  checkITemType;
  totalCount;
  sacCodeData;
  sacCodeDetails = [];
  date;
  sacCodePrice;
  sort_order = 0;
  addItemModelRef;
  checkSplitAmount = false;
  changeInvoiceForm: any = {};
  checkRedoQRDate = false;
  disableEmailBtn = false;
  errorBtn = false;
  getSacCode;
  checkConvertToB2B = false;
  irnObject: any = {};
  printEnable = false;
  emailPdf = false;
  loginUSerRole;
  sacEditForHICC = true;
  suptyp;
  redoQRKey = false;
  taxableArr = [];
  address1_state;
  address2_state: any;
  location_state: any;
  today_date: any;
  hindia_prop = 'HINDIA-01'//JP-2022
  editLineItemInvoiceInfo;
  invoicesList: any = []
  item_name;
  pos_bill_data;
  item: any
  selectAll: any;
  userName;
  signature_img: any = {}
  signature_pfx: any = {}
  pfx_password;
  UserSignature: any = {};
  tabType: any = 'pfx';
  eTaxInvoiceDownloadBtn: any;
  syncList: any = {}
  checkIRNdate :any = false;

  constructor(
    private modal: NgbModal,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private route: Router,
    private userService: UserService,
    private sanitizer: DomSanitizer,
    private toastr: ToastrService,
    private location: Location,
    config: NgbNavConfig,
  ) {
    config.destroyOnHide = false;
    config.roles = false;
  }

  ngOnInit(): void {
    this.stateCodes = stateCode;
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    console.log(this.companyDetails.vat_reporting)
    this.companyDetails['pan_number'] = this.companyDetails?.gst_number.substr(2, 10);
    this.getInvoiceInfo();
    this.getPermissions();

    this.params = this.activatedRoute.snapshot.queryParams;
    this.invoiceNumber = this.activatedRoute.snapshot.params.id;
    this.loginData = JSON.parse(localStorage.getItem('login'))
    if (this.loginData?.name == 'Administrator') {
      this.loginUSerRole = true;
    } else {
      this.loginUSerRole = this.loginData.rolesFilter.some((each: any) => (each == 'ezy-Finance'))
      console.log("loginUSerRole == ", this.loginUSerRole)
      if (this.companyDetails?.property_group == "HolidayIn Express") {
        let sacEditRolesForHICC = this.loginData.rolesFilter.filter((each: any) => (each !== 'ezy-FrontOffice'))
        this.sacEditForHICC = sacEditRolesForHICC.length > 0 ? true : false;
      }

    }
    this.enableETaxInvoiceDownloadBtn()
  }
  getInvoiceInfo() {
    return new Promise((resolve, reject) => {
      const params = this.activatedRoute.snapshot.params;
      if (params.id) {
        this.http.get(ApiUrls.invoices + '/' + params.id).subscribe((res: any) => {
          const temp = this.invoiceInfo.credit_note_items || [];
          if (res.data?.invoice_object_from_file) {
            res.data.invoice_object_from_file = JSON.parse(res.data.invoice_object_from_file)?.data || []
          }
          this.invoiceInfo = { ...res.data };
          this.getGSTDetailsbyInvoice()

          let today_date: any = Moment(this.invoiceInfo?.invoice_date).format('YYYY-MM-DD')
          let date_expiry: any = this.companyDetails?.einvoice_missing_start_date ? Moment(this.companyDetails?.einvoice_missing_start_date).format('YYYY-MM-DD') : null
          
          if (this.companyDetails?.einvoice_missing_date_feature && (today_date >= date_expiry)) {
            let today_date: any = Moment(new Date()).format('YYYY-MM-DD') // new Date()
            let date_expiry: any = Moment(Moment(this.invoiceInfo.invoice_date).add(7, 'd').format('YYYY-MM-DD')) //new Date(this.invoiceInfo.invoice_date);
            date_expiry = Moment(date_expiry).format('YYYY-MM-DD')
            this.invoiceInfo['expiry_date'] = Moment(date_expiry).format('YYYY-MM-DD') //date_expiry
            this.invoiceInfo['expiry_days'] = Moment(date_expiry).diff(Moment(today_date), 'days') // Math.round(Math.abs((date_expiry - today_date) / oneDay))            
            this.checkIRNdate = date_expiry < today_date
          }
          this.changeInvoiceForm = { ...res.data };
          this.maxItemDate = Moment(new Date(this.changeInvoiceForm.invoice_date)).format('YYYY-MM-DD');;
          this.sez = this.invoiceInfo?.sez == 1 ? true : false;
          this.lut = this.invoiceInfo?.lut == 1 ? true : false;
          if (res?.data?.irn_generated == 'Error' && res?.data?.error_message) {
            let code = res?.data?.error_message
            let sacNotFound = code.match('SAC Code')
            if (sacNotFound?.length > 0) {
              this.errorBtn = sacNotFound.length > 0 ? true : false;
              this.getSacCode = code.substring(
                code.lastIndexOf("SAC Code") + 9,
                code.lastIndexOf("not found")
              );
            }
          }
          if (res.data?.qr_code_image == '' || res.data?.b2c_qrimage == '') {
            this.redoQRKey = false;
          } else if (res?.data?.qr_code_image || res?.data?.b2c_qrimage) {
            this.redoQRKey = false;
          } else {
            this.redoQRKey = true;
          }
          // this.invoiceInfo['error_message'] = res.data?.error_message.substring(1, res.data?.error_message.length-1)
          //  console.log( res.data?.error_message.substring(1, res.data?.error_message.length-1))
          this.invoiceInfo['place_of_supply_name'] = stateCode.find((each) => each.tin == this.invoiceInfo.place_of_supply);
          if (res.data.irn_generated === 'Pending' || res.data.irn_generated === 'Error') {
            if (this.invoiceInfo?.items.length > 0) {
              let checkToRe_process = this.invoiceInfo?.items[0]?.sac_index && (this.invoiceInfo?.irn_generated == 'Pending' || this.invoiceInfo?.irn_generated == 'Error') ? false : true;
              if (checkToRe_process) {
                this.reload(this.invoiceInfo?.invoice_file, false)
              }
            }
          }

          if (this.invoiceInfo?.place_of_supply === null || this.invoiceInfo?.place_of_supply === 'NA') {
            this.checkPOS();
          }
          this.stateCode = stateCode.find((res: any) => res.tin === this.invoiceInfo.state_code)
          // this.previewFile = this.invoiceInfo?.invoice_file;
          this.invoiceInfo['creditSummary'] = temp;
          this.invoiceInfo.gst_summaryTotal = (this.invoiceInfo.gst_summary as any[]).reduce((prev, nxt) => prev + parseFloat(nxt.amount), 0);
          const generatedTime = new Date(this.invoiceInfo.irn_generated_time);
          // const generatedTime = this.invoiceInfo.irn_generated_time;
          if (this.invoiceInfo?.irn_generated_time) {
            let xyz: any = Moment(this.invoiceInfo?.irn_generated_time).add(24, 'hours').format('YYYY-MM-DD HH:mm:ss');
            let currentDt: any = Moment(new Date()).format('YYYY-MM-DD HH:mm:ss');
            console.log("xyz ===", xyz, " +++++++++++++ ", this.invoiceInfo.irn_generated_time, " ======= ", currentDt)
            this.invoiceInfo['showCancelIrn'] = Date.parse(xyz) >= Date.parse(currentDt);
            console.log("=======", this.invoiceInfo.showCancelIrn)
          }

          // generatedTime.setTime(generatedTime.getTime() + (25 * 60 * 60 * 1000));
          // let cancelIRNTime = new Date(new Date(generatedTime).getTime() + 60 * 60 * 24 * 1000);
          // console.log("=======",cancelIRNTime,generatedTime)

          let end = Moment(this.invoiceInfo?.ack_date).add(2, 'days');
          this.checkRedoQRDate = Moment().isBefore(end);
          resolve(true);
          if (this.invoiceInfo?.items) {
            this.selectAll = this.invoiceInfo.items.every(res => res.lut_exempted)
            this.sortedListInvoice = this.invoiceInfo.items.sort((a, b) => parseFloat(a.sort_order) - parseFloat(b.sort_order));
            this.pdfListItems = this.invoiceInfo.items.sort((a, b) => parseFloat(a.sort_order) - parseFloat(b.sort_order));
            this.sacCodeDetails = this.invoiceInfo.items.sort((a, b) => parseFloat(a.sort_order) - parseFloat(b.sort_order))

            let nonGroupedArr = [...this.invoiceInfo.items];

            const keys_to_keep = ['item_value', 'sac_code', 'cgst_amount', 'sgst_amount', 'igst_amount', 'cess', 'cess_amount', 'vat_amount', 'taxable'];

            const redux = array => array.map(o => keys_to_keep.reduce((acc, curr) => {
              acc[curr] = o[curr];
              return acc;
            }, {}));

            let testArr = redux(nonGroupedArr)
            testArr = testArr.filter((each: any) => {
              return each.taxable === "Yes";
            })
            this.taxableArr = Object.values(testArr.reduce((acc, { item_value, cgst_amount, sgst_amount, igst_amount, cess, cess_amount, vat_amount, taxable, ...r }) => {

              let key = Object.entries(r).join('-');
              acc[key] = (acc[key] || { ...r, item_value: 0, cgst_amount: 0, sgst_amount: 0, igst_amount: 0, cess: 0, cess_amount: 0, vat_amount: 0 });
              return (acc[key].item_value += item_value, acc[key].cgst_amount += cgst_amount, acc[key].sgst_amount += sgst_amount, acc[key].igst_amount += igst_amount, acc[key].cess += cess, acc[key].cess_amount += cess_amount, acc[key].vat_amount += vat_amount, acc);

            }, {}));

            if ((this.companyDetails.name == "FMCOMR-01" || this.companyDetails.name == 'FPBSA-01' || this.companyDetails.name == 'HRC-01' || this.companyDetails.name == 'JWMC-01') && this.invoiceInfo?.irn_generated == "Success" && this.invoiceInfo?.invoice_type == "B2B") {
              this.getIrnObjectSuccess();
            }

          }
          // if (this.invoiceInfo?.docstatus === 2) {
          //   this.http.get(`${ApiUrls.cancelledInvoiceDetails}/${this.invoiceInfo?.invoice_number}`).subscribe((res: any) => {

          //     this.invoiceInfo.irn_generated = res?.data?.irn_generated;
          //     this.invoiceInfo.irn_cancelled = res?.data?.irn_cancelled;
          //   })
          // }

        });
      }
    });
  }

  getGSTDetailsbyInvoice() {
    this.http.get(ApiUrls.taxPayerDefault + '/' + this.invoiceInfo?.company_gst).subscribe((res: any) => {
      if (res && res?.data && res?.data?.name) {
        console.log(res);
        this.invoiceInfo['company_fssai_number'] = this.companyDetails?.fssai_number;
        this.invoiceInfo['company_name'] = this.companyDetails?.company_name
        this.invoiceInfo['company_legal_name'] = res?.data?.legal_name;
        this.invoiceInfo['company_address_1'] = res?.data?.address_1
        this.invoiceInfo['company_address_2'] = res?.data?.address_2;
        this.invoiceInfo['company_location'] = res?.data?.location;
        this.invoiceInfo['company_pincode'] = res?.data?.pincode;
        this.invoiceInfo['company_state_code'] = res?.data?.state_code;
        this.invoiceInfo['company_logo'] = this.companyDetails?.company_logo
        this.invoiceInfo['company_place_of_supply'] = res?.data?.state_code;
        this.invoiceInfo['custom_e_tax_invoice_logo_image'] = this.companyDetails?.custom_e_tax_invoice_logo_image
      }
    })
  }

  checkPOS() {
    let dataObj = {
      place_of_supply: this.companyDetails?.state_code
    }
    this.http.put(ApiUrls.invoices + '/' + this.invoiceInfo.name, dataObj).subscribe((res) => {

      this.getInvoiceInfo();
    });
  }

  getPermissions(): void {
    const params = this.activatedRoute.snapshot.params
    if (!params) { return; }
    const queryParams: any = {};
    queryParams.doctype = "Invoices";
    queryParams.name = params.id
    this.http.get(ApiUrls.permissions, { params: queryParams }).subscribe((res: any) => {
      this.userService.setUser(res)
    })
  }

  // getCreditSummary(): void {
  //   const params = {
  //     filters: JSON.stringify([['parent', '=', this.activatedRoute.snapshot.params.id]]),
  //     fields: JSON.stringify(['name', 'creation', 'item_name', 'item_vuploadFilealue_after_gst', 'sac_code', 'item_value', 'cgst', 'cgst_amount', 'sgst', 'sgst_amount', 'igst', 'igst_amount', 'item_taxable_value'])
  //   };
  //   this.http.get(ApiUrls.creditNoteSummary, { params: params as any }).subscribe((res: any) => {
  //     this.invoiceInfo['creditSummary'] = res.data;
  //   });
  // }
  onTabChange(event: number) {
    this.sortedListInvoice = []
    this.navNumber = event
    if (event === 4) {
      if (this.invoiceInfo?.has_credit_items === 'Yes') {
        this.sortedListInvoice = this.invoiceInfo.items.filter((each: any) => each.item_mode === "Credit")
        this.sortedListInvoice = this.sortedListInvoice.sort((a, b) => parseFloat(a.sort_order) - parseFloat(b.sort_order));
      }
      if (this.invoiceInfo?.has_discount_items === 'Yes') {
        this.sortedListInvoice = this.invoiceInfo.items.filter((each: any) => each.item_mode === "Discount")
        this.sortedListInvoice = this.sortedListInvoice.sort((a, b) => parseFloat(a.sort_order) - parseFloat(b.sort_order));
      }
    }
    if (event === 1) {
      this.sortedListInvoice = []
      if (this.invoiceInfo?.items) {
        this.sortedListInvoice = this.invoiceInfo.items.sort((a, b) => parseFloat(a.sort_order) - parseFloat(b.sort_order));
      }
    }
  }

  invoiceEdit(content): void {
    this.editData = JSON.parse(JSON.stringify(this.invoiceInfo));
    this.modal.open(content, {
      size: 'lg',
      centered: true
    });
  }

  taxEdit(taxModal): void {
    this.checkConvertToB2B = true;
    this.taxPayerDetails = JSON.parse(JSON.stringify(this.invoiceInfo));
    this.checkApiMethod = false;
    this.modal.open(this.B2CtoB2CTemp, {
      // size: 'lg',
      centered: true
    });
  }

  /**Sez Generate IRN Functionality */
  sezGenerateIRNFunc(form: NgForm, modal) {
    let dataObj = {
      suptyp: form.value.SEZWP || form.value.SEZWOP
    }
    if (dataObj) {
      this.http.put(`${ApiUrls.invoices}/${this.invoiceInfo.invoice_number}`, dataObj).subscribe((res: any) => {
        if (res.data) {
          const dataObj = {
            invoice_number: this.invoiceInfo.name,
            generation_type: 'Manual'
          }
          this.http.post(ApiUrls.generateIrn_new, { data: dataObj }).subscribe(async (res: any) => {
            if (res.message.success) {
              await this.getInvoiceInfo();
              this.toastr.success("IRN generated successfully")
              modal.close();
            } else {
              this.toastr.error(res.message.message);
              if (res?.message?.message == '2163 : The document date should not be future date .') {
                this.modal.open(this.invoiceDateRef, { size: 'sm' });
              }
            }
          }, (err) => {
            console.log('err: ', err);

          });
        }
      })
    }
  }
  /**Generate IRN */
  generateIrn(): void {
    if (this.companyDetails?.einvoice_missing_date_feature) {
      this.http.post(ApiUrls.validate_irn_gen_date, { "invoice_number": this.invoiceInfo?.invoice_number }).subscribe((resp: any) => {
        if (resp?.message?.success) {
          this.generateIRNFn()
        } else {
          this.toastr.error("IRN Generation Date is expired")
        }
      })
    } else {
      this.generateIRNFn()
    }
  }

  generateIRNFn() {
    if (this.invoiceInfo.sez == 1) {
      let modal = this.modal.open(this.sezGenerateIRN, {
        centered: true, size: 'md', backdrop: 'static'
      })
      if (this.invoiceInfo.total_gst_amount == 0) {
        this.invoiceInfo.suptyp = 'SEZWOP'
      } else if (this.invoiceInfo.total_gst_amount > 0) {
        this.invoiceInfo.suptyp = 'SEZWP'
      }
    } else {
      if (this.invoiceInfo.has_credit_items == 'Yes' && this.companyDetails.auto_adjustment == 'Manual') {
        window.alert("Please adjust the allowances to generate IRN");
      } else if (this.companyDetails?.auto_adjustment == 'Automatic' && this.invoiceInfo?.has_credit_items == 'Yes') {
        window.alert("You have a pending adjustment in the invoice");
      }
      else if (!window.confirm(`Are you sure to generate IRN number for Invoice ${this.invoiceInfo.name} ?`)) {
        return null;
      } else {
        const dataObj = {
          invoice_number: this.invoiceInfo.name,
          generation_type: 'Manual'
        }
        this.http.post(ApiUrls.generateIrn_new, { data: dataObj }).subscribe(async (res: any) => {
          if (res.message.success) {
            await this.getInvoiceInfo();
            // this.submitInvoice();
            this.toastr.success("IRN generated successfully")
          } else {
            this.toastr.error(res.message.message);
            if (res?.message?.message.includes('3075 : GSTIN')) {
              this.http.put(`${ApiUrls.invoices}/${this.invoiceInfo?.invoice_number}`, {
                irn_generated: 'Error', error_message: res.message.message
              }).subscribe((res: any) => this.getInvoiceInfo())
            }
            if (res?.message?.message == '2163 : The document date should not be future date .') {
              this.modal.open(this.invoiceDateRef, { size: 'sm' });
            }
          }
        }, (err) => {
          console.log('err: ', err);

        });
      }
    }
  }

  updateInvoiceDate(form: NgForm, modal) {
    if (form.valid) {
      const date = Moment(form.value.invoice_date).format('YYYY-MM-DD');
      this.http.put(ApiUrls.invoices + `/` + this.invoiceInfo.name, { invoice_date: date }).subscribe((res: any) => {
        if (res.data) {
          this.toastr.success("Invoice date updated successfully");
          this.getInvoiceInfo();
          modal.close();
        } else {
          this.toastr.error(res.message.message);
        }
      })
    } else {
      form.form.markAllAsTouched();
    }
  }
  generateQr(): void {
    if (!window.confirm(`Are you sure to generate QR number for Invoice ${this.invoiceInfo.name} ?`)) {
      return null;
    } else {
      const formData = new FormData();
      // formData.append('method', 'send_invoicedata_to_gcb');
      // formData.append('args', `{"invoice_number":"${this.invoiceInfo.name}"}`);
      // formData.append('docs', JSON.stringify(this.invoiceInfo));
      formData.append('invoice_number', this.invoiceInfo.invoice_number)
      this.http.post(ApiUrls.generateQR, formData).subscribe(async (res: any) => {
        if (!res.message.success) {
          this.toastr.error(res.message.message)
        }
        if (res.message.success) {
          await this.getInvoiceInfo();
          this.toastr.success("QR generated successfully")
        }

      });
    }
  }
  // reInitiateInvoice(): void {
  //   if (!window.confirm(`Are you sure to Re-Initiate Irn number for Invoice Number ${this.invoiceInfo.name} ?`)) {
  //     return null;
  //   } else {
  //     const formData = new FormData();
  //     formData.append('method', 'generateIrn');
  //     formData.append('args', `{"invoice_number":"${this.invoiceInfo.name}"}`);
  //     formData.append('docs', JSON.stringify(this.invoiceInfo));
  //     this.http.post(ApiUrls.generateIrn, formData).subscribe((res) => {
  //       this.getInvoiceInfo();
  //     });
  //   }
  // }

  cancelIrn(): void {
    if (!window.confirm(`Are you sure to cancel IRN for Invoice Number ${this.invoiceInfo.name} ?`)) {
      return null;
    } else {
      const reason = window.prompt('Please Enter Reason');
      if (reason == null) {
        return null;
      }
      const formData = new FormData();
      formData.append('method', 'cancelIrn');
      formData.append('reason', reason);
      formData.append('args', JSON.stringify({ invoice_number: this.invoiceInfo.name, reason }));
      let info = { ...this.invoiceInfo }
      info.invoice_object_from_file = ""
      formData.append('docs', JSON.stringify(info));
      this.http.post(ApiUrls.generateIrn, formData).subscribe(async (res) => {
        await this.getInvoiceInfo();
        await this.submitInvoice();
      });


      /****** api Changed */

      // this.http.get(ApiUrls.generateIrn,{params:{invoice_number:this.invoiceInfo.name,reason:reason}}).subscribe( async(res:any)=>{
      //   if(res){
      //     await this.getInvoiceInfo();
      //     await this.submitInvoice();
      //   }
      // })
    }
  }

  private submitInvoice(): void {
    const formData = new FormData();
    formData.append('method', 'frappe.client.submit');
    formData.append('args', JSON.stringify({ doctype: Doctypes.invoices, name: this.invoiceInfo.name }));
    // formData.append('doc', JSON.stringify(this.invoiceInfo));
    let info = { ...this.invoiceInfo }
    info.invoice_object_from_file = ""
    formData.append('doc', JSON.stringify(info));
    formData.append('docname', JSON.stringify(this.invoiceInfo.name));
    formData.append('doctype', JSON.stringify(Doctypes.invoices));
    this.http.post(ApiUrls.permanentInvoice, formData).subscribe(async (res) => {
      // await this.getInvoiceInfo();
      this.frappeCancelIrn();
    });
  }

  private frappeCancelIrn(): void {
    const formData = new FormData();
    formData.append('doctype', Doctypes.invoices);
    formData.append('name', this.invoiceInfo.name);
    this.http.post(ApiUrls.frappeCancelIrn, formData).pipe((switchMap((res) => {
      const temp = new FormData();
      temp.append('doctype', Doctypes.invoices);
      temp.append('docname', this.invoiceInfo.name);
      return this.http.post(ApiUrls.amendDoc, temp);
    }))).subscribe((res) => {
      this.getInvoiceInfo();
    });

  }

  onInvoiceSubmit(form: NgForm, modalRef): void {
    if (form.valid) {
      this.http.put(ApiUrls.invoices + '/' + this.invoiceInfo.name, form.value).subscribe((res) => {
        modalRef.close();
        this.getInvoiceInfo();
      });
    } else {
      form.form.markAllAsTouched();
    }
  }
  onTaxSubmit(form: NgForm, modalRef): void {
    if (form.valid) {
      this.http.put(ApiUrls.invoices + '/' + this.invoiceInfo.name, form.value).subscribe((res) => {
        modalRef.close();
        this.getInvoiceInfo();
      });
    } else {
      form.form.markAllAsTouched();
    }
  }

  openMenu() {
    const modalRef = this.modal.open(ActivitylogComponent, {
      size: 'md',
      centered: true,
      windowClass: 'sideMenu',
    })
    modalRef.componentInstance.invoiceNumber = this.invoiceNumber;
    modalRef.componentInstance.docName = 'Invoices';
  }

  // getActivityLogs() {
  //   const params = this.activatedRoute.snapshot.params;
  //   this.http.get(ApiUrls.resource + '/Version', {
  //     params: {
  //       filters: [JSON.stringify([['docname', '=', params.id]])],
  //       fields: JSON.stringify(['data', 'name', 'creation', 'modified_by']),
  //       order_by: `${'creation desc'}`,
  //     }
  //   }).subscribe((res: any) => {
  //     if (res.data) {
  //       this.activityLogs = (res.data as any[]).map((each) => {
  //         each.data = JSON.parse(each.data);
  //         return each;
  //       });
  //       this.activityLog = this.activityLogs[0];
  //     }
  //   });
  // }

  copyToClipboard(item) {
    this.isCopy = !this.isCopy;
    document.addEventListener('copy', (e: ClipboardEvent) => {
      e.clipboardData.setData('text/plain', (item));
      e.preventDefault();
      document.removeEventListener('copy', null);
    });
    document.execCommand('copy');
  }

  reInitiateInvoice() {
    this.errorMessage = null;
    this.successMessage = ''
    this.filename = '';
    const modalRef = this.modal.open(this.uploadModal, {
      size: 'md',
      centered: true
    });
    // modalRef.result.then(() => {
    //   this.getInvoiceInfo();
    // })
  }

  handleFileInput(files: File[]) {
    this.filename = files[0].name;
    this.fileToUpload = files[0];
    var reader = new FileReader();
    reader.readAsDataURL(this.fileToUpload);
    reader.onload = (_event) => {
      this.imgURL = reader.result;
    }
  }

  uploadService() {
    if (this.fileToUpload) {
      const params = this.activatedRoute.snapshot.params;
      const formData = new FormData();
      formData.append('file', this.fileToUpload, this.fileToUpload.name);
      formData.append('is_private', '1');
      formData.append('folder', 'Home');
      // formData.append('fieldname', 'invoice');
      // formData.append('doctype', Doctypes.invoices);
      formData.append('docname', params.id);
      this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
        if (res.message?.file_url) {
          this.reload(res.message?.file_url)
        } else {
          console.log(res)
        }
      })
    }
  }

  reload(item, invoke = true) {
    if (this.invoiceInfo.invoice_file == '' && this.invoiceInfo.invoice_from == 'File') {
      this.http.post(ApiUrls.reprocessBulkUpload, { data: { invoice_number: this.invoiceInfo.name } }).subscribe((res: any) => {
        if (res.message.success) {
          this.toastr.success("Success")
          this.getInvoiceInfo();
        } else {
          this.getInvoiceInfo();
          this.toastr.error()
        }
      })
    } else {
      let api = this.companyDetails?.new_parsers == 0 ? `${ApiUrls.reinitiate}` : `${ApiUrls.new_reinitiate}`
      this.http.post(`${api}${this.companyDetails?.name}.${'reinitiate_parser.reinitiateInvoice'}`, { data: { 'filepath': item, 'invoice_number': this.invoiceInfo?.invoice_number } }).subscribe((res: any) => {
        if (res.message.success) {
          this.successMessage = res.message;
          if (invoke) {
            this.getInvoiceInfo();
          }
          setTimeout(() => {
            this.modal.dismissAll()
          }, 500);
        } else {
          this.getInvoiceInfo();
          this.errorMessage = res.message;
        }
      })
    }
  }
  print() {
    let printData = localStorage.getItem('printer');

    this.http.post(ApiUrls.print, { invoiceNumber: this.invoiceInfo?.invoice_number, printer: printData }).subscribe((res: any) => {
      if (res?.message?.success) {
        this.toastr.success(res?.message?.message)
      }
    })
  }

  SyncErrorLogs(submodel, invoice) {
    this.modal.open(submodel, { size: 'lg', centered: true, })
    this.syncList = this.invoiceInfo;
  }


  // printInvoice(type) {
  //   if (type == "Invoice") {
  //     let objFra = document.getElementById('iframe') as HTMLIFrameElement;
  //     if (objFra) {
  //       objFra.contentWindow.print();
  //     }

  //   }
  //   if (type == "InvoiceQR") {
  //     let objFra = document.getElementById('invoiceWithQr') as HTMLIFrameElement;
  //     if (objFra) {
  //       objFra.contentWindow.print();
  //     }
  //   }
  //   if (type == "InvoiceQRB2C") {
  //     let objFra = document.getElementById('invoiceWithQrB2C') as HTMLIFrameElement;
  //     if (objFra) {
  //       objFra.contentWindow.print();
  //     }
  //   }
  //   if (type == "CreditQR") {
  //     let objFra = document.getElementById('creditNoteQr') as HTMLIFrameElement;
  //     if (objFra) {
  //       objFra.contentWindow.print();
  //     }
  //   }
  // }




  saveSignature(modal) {
    let data;
    console.log('=====', this.pfx_password)
    if (this.tabType == 'pfx') {
      data = {
        signature_pfx: this.signature_pfx,
        users: this.userName,
        pfx_password: this.pfx_password
      }
    } else if (this.tabType == 'image') {
      data = {
        signature_image: this.signature_img,
        users: this.userName
      }
    }
    // this.http.post(`${ApiUrls.resource}/${Doctypes.userSignature}`, data).subscribe((res: any) => {
    //   if (res?.data) {
    //     console.log('=======', this.UserSignature)
    //     this.toastr.success("Updated");
    //     this.UserSignature = res.data;
    //     this.modal.dismissAll();
    //   }
    // })
    this.http.get(`${ApiUrls.resource}/${Doctypes.userSignature}`, {
      params: {
        filters: JSON.stringify([['name', '=', this.userName]]),
        fields: JSON.stringify(['*'])
      }
    }).subscribe((res: any) => {
      if (res?.data) {
        if (res.data[0]?.signature_image || res.data[0]?.signature_pfx) {
          this.http.put(`${ApiUrls.resource}/${Doctypes.userSignature}/${res.data[0]?.name}`, data).subscribe((res: any) => {
            this.toastr.success("uploaded");
            this.UserSignature = res.data;
          })
        } else {
          this.http.post(`${ApiUrls.resource}/${Doctypes.userSignature}`, data).subscribe((res: any) => {
            console.log(res?.data)
            this.toastr.success("Uploaded");
          })
        }
      }
    })
  }

  printSignInvoice() {
    let data = {
      invoice_number: this.invoiceInfo.invoice_number,
      // based_on: 'user'
    }
    this.http.post(ApiUrls.e_signature, data).subscribe((res: any) => {
      if (res?.message?.success) {
        // this.toastr.success(res?.message?.message)
        // const fileUrl = `${environment.apiDomain}${res?.message?.file}`
        // window.open(fileUrl, '_blank');
        console.log('=====', res?.file)
        let path = res?.message?.file;
        var link = document.createElement('a');
        link.href = `${this.apiDomain}${res.message.file}`;
        link.download = path;
        link.target = "_blank";
        link.click()
      }
    })
  }


  synctoGST() {
    let data = {
      invoice_number: this.invoiceInfo.invoice_number,
      doctype: Doctypes.invoices
    }
    this.http.post(ApiUrls.sync_data_to_erp_single, data).subscribe((res: any) => {
      if (res.message.success) {
        this.toastr.success(res.message.message);
        this.getInvoiceInfo();
      } else {
        this.toastr.error(res.message.message)
      }
    });
  }



  async printInvoice(type) {
    await this.fileType(type);
    if (this.previewFile.includes('/private/')) {
      print({
        printable: this.previewFile,
        type: 'pdf'
      })
    } else {
      print({
        printable: this.previewFile.split(',')[1],
        type: 'pdf',
        base64: true,
      });
    }
  }
  generatePdf(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (this.invoiceInfo?.has_credit_items == "Yes" && this.invoiceInfo?.invoice_type == "B2B") {
          var div = document.getElementById('pmsCreditPDF');
        } else if (this.invoiceInfo?.has_credit_items == "No" && this.invoiceInfo?.invoice_type == "B2B") {
          var div = document.getElementById('PmsTaxPdf');
        } else {
          var div = document.getElementById('pmsPDF');
        }
        const pdfEle = div.querySelector('.pdf-display');
        pdfEle.classList.remove('pdf-display');
        html2canvas(div).then(async (canvas) => {
          var imgWidth = 208;
          var imgHeight = canvas.height * imgWidth / canvas.width;
          const contentDataURL = canvas.toDataURL('image/png')
          let pdf = new jsPDF('p', 'mm', 'a4', true);
          var position = 0;
          await pdf.addImage(contentDataURL, 'PNG', 0, position, imgWidth, imgHeight);
          const blob = await pdf.output('blob');
          pdfEle.classList.add('pdf-display');
          resolve(blob);
        });
      }, 1000)
    })

  }
  async openEmailTemp() {
    this.emailPdf = true;
    this.emailTempData.attachments = [];
    this.disableEmailBtn = false;
    let filesToBeUpload = [];
    if (this.invoiceInfo?.invoice_from == "Pms") {
      if (this.invoiceInfo?.has_credit_items == "Yes") {
        filesToBeUpload.push('Tax Invoice', 'E-credits');
      } else {
        filesToBeUpload.push('Tax Invoice');
      }
    } else {
      if (this.invoiceInfo?.invoice_type == 'B2B') {
        if (this.invoiceInfo?.has_credit_items == "Yes") {
          filesToBeUpload.push('E-Tax', 'E-Credit');
        } else {
          filesToBeUpload.push('E-Tax');
        }
      } else {
        filesToBeUpload.push('PMS Invoice');
      }
    }
    let filesForEmailTemp = [];
    filesToBeUpload.forEach(async (each: any, index) => {
      const formData = new FormData();
      if (this.invoiceInfo?.invoice_from == 'File') {

        // if (each == 'E-Credit') {
        //   const file = await this.generatePdf();
        //   formData.append('file', file, 'e-credit.pdf');
        // }
        // if (each == 'E-Tax') {
        //   const file = await this.generatePdf();
        //   formData.append('file', file, 'e-tax.pdf');
        // }
        // if (each == 'PMS Invoice') {
        //   const file = await this.generatePdf();
        //   formData.append('file', file, 'pms.pdf');
        // }
        const file = await this.generatePdf();
        formData.append('file', file, `${each}.pdf`);
      } else {
        if (this.invoiceInfo?.has_credit_items == "Yes" && each == 'E-credits') {
          const file = await this.generatePdf();
          formData.append('file', file, 'credit.pdf');
        } else {
          const fileAsArray: any = await this.fileType(each, true);
          formData.append('file', new Blob([fileAsArray], { type: "application/pdf" }), Date.now() + 'with-qr.pdf');
        }
      }
      formData.append('is_private', '1');
      formData.append('folder', 'Home');
      // formData.append('doctype', Doctypes.invoices);
      // formData.append('fieldname', 'invoice');
      formData.append('docname', this.invoiceInfo.name);
      this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
        if (res) {
          filesForEmailTemp.push(res.message.name)
          if (index + 1 == filesToBeUpload.length) {
            this.http.post(ApiUrls.emailTemplates, {
              invoice_number: this.invoiceInfo.invoice_number,
              templateFiles: filesForEmailTemp
            }).subscribe((data: any) => {
              if (data.message) {
                this.emailTempData = data.message;
                this.emailTempData.deleteFile = filesForEmailTemp;
                console.log(this.emailTempData?.val?.recipients, this.invoiceInfo?.email)
                if (this.invoiceInfo?.email) {
                  this.emailTempData.val.recipients = this.invoiceInfo?.email;
                  // console.log(this.invoiceInfo?.email, this.emailTempData.val.recipients)
                } else {
                  this.emailTempData.val.recipients = this.invoiceInfo?.email;
                  // console.log(this.invoiceInfo?.email, this.emailTempData.val.recipients)
                }
                // if (this.emailTempData?.val?.recipients) {
                //   console.log(this.invoiceInfo?.email)

                // }
              } else {
                this.toastr.error()
              }

            });
          }
        } else {
          this.toastr.error()
        }
      })
    })



    let modal = this.modal.open(this.emailTemp, { centered: true, size: 'lg' });
    modal.result.then((res) => '', () => '').catch((err) => err).finally(() => {
      /* delete pdf api goes here */
      // this.emailTempData.deleteFile.map((each:any)=>{
      //   this.http.delete(`${ApiUrls.resource}/${Doctypes.file}/${each}`).subscribe((res: any) => {
      //   });
      // })

    })

  }

  async emailForm(form: NgForm, modalRef) {
    if (form.valid) {
      const formData = new FormData();
      formData.append('recipients', this.emailTempData?.val?.recipients);
      formData.append('subject', this.emailTempData?.val?.subject);
      formData.append('content', this.emailTempData?.val?.use_html == 1 ? this.emailTempData?.val?.response_html : this.emailTempData?.val?.response);
      formData.append('doctype', Doctypes.invoices);
      formData.append('name', this.invoiceInfo?.invoice_number);
      formData.append('attachments', JSON.stringify(this.emailTempData?.attachments))
      // formData.append('base64', this.previewFile)
      formData.append('send_email', "1");
      // formData.append('print_html', null);
      formData.append('send_me_a_copy', "0");
      // formData.append('print_format', "Standard");
      formData.append('email_template', this.emailTempData?.val?.name);
      formData.append('read_receipt', "0");
      formData.append('now', "true");
      // formData.append('attach_document_print', "0");
      this.disableEmailBtn = true;
      this.http.post(ApiUrls.sendEmail, formData).subscribe((res: any) => {
        // this.disableEmailBtn = true;
        if (res.message) {
          setTimeout(() => {
            this.http.get(`${ApiUrls.resource}/${Doctypes.emailLogs}`, {
              params: {
                fields: JSON.stringify(['reference_name', 'name', 'status']),
                filters: JSON.stringify([['reference_name', '=', this.invoiceInfo.name], ['status', '!=', 'Sent']])
              }
            }).subscribe((res: any) => {
              this.toastr.success('Email Successfully Sent');
              this.modal.dismissAll();
              // const formData = new FormData();
              // formData.append('name', res.data[0].name);
              // this.http.post(`${ApiUrls.sendEmailQueue}`, formData).subscribe((res: any) => {
              //   this.toastr.success('Email Successfully Sent');
              //   this.modal.dismissAll();
              // })
            })
          }, 3000);
        } else {
          this.toastr.error()
        }
      })
    } else {
      form.form.markAllAsTouched();
    }
  }
  onChangeEmailTemp(): void {
    let formData = new FormData();
    formData.append('template_name', this.emailTempData.template_name);
    formData.append('doc', JSON.stringify(this.invoiceInfo))
    this.http.post(ApiUrls.getEmailTempData, formData).subscribe((res: any) => {
      this.emailTempData.subject = res.message.subject;
      this.emailTempData.message = res.message.message;
    })
  }

  getInvoiceFileNames(fileArr): void {
    this.fileName = []
    let files = fileArr.filter((each: any) => each !== undefined)
    files.forEach(element => {
      this.http.get(ApiUrls.filesPath, {
        params: {
          filters: JSON.stringify([["file_url", "=", element]])
        }
      }).subscribe((res: any) => {
        this.fileName.push(res.data[0].name)
      })
    });
  }

  /**Convert B2C to B2C  */

  openConvertModal(): void {

    // this.http.post(ApiUrls.validate_irn_gen_date, { "invoice_number": this.invoiceInfo?.invoice_number }).subscribe((resp: any) => {
    //   if (resp?.message?.success) {

    this.taxPayerDetails = {};
    this.checkConvertToB2B = false;
    this.checkApiMethod = false;
    let modal = this.modal.open(this.B2CtoB2CTemp, { centered: true, size: 'md' })


    this.taxPayerDetails.company = this.companyDetails?.name
    //     }else{
    //       this.toastr.error("IRN Generation Date is expired")
    //     }
    // })
  }
  changeDescription(e): void {
    if (e.length == 15) {
      this.http.get(`${ApiUrls.getClient}?doctype=${Doctypes.TaxPayerDetail}&fieldname=name&filters=${e}`).subscribe((res: any) => {
        if (res.message?.name) {
          this.checkName = true;
        } else {
          this.checkName = false
        }
      })
    } else {
      this.checkApiMethod = false;
    }
  }
  onSubmit(form: NgForm) {
    let login: any = JSON.parse(localStorage.getItem('login'))
    if (form.valid) {
      if (!this.checkApiMethod) {
        const dataObj = { "data": { "code": form.value.company, "gstNumber": form.value.gst_number } }
        this.http.post(`${ApiUrls.taxPayersDetails}`, dataObj).subscribe((res: any) => {
          try {
            if (res.message.success) {
              this.checkApiMethod = true;
              this.apiMethod = res.message.update;
              this.taxPayerDetails = res.message.data
            } else {
              this.toastr.error(res.message.message);
            }
          } catch (e) { console.log(e) }
        })
      } else {
        const updateGstNum = this.http.put(`${ApiUrls.taxPayerDefault}/${this.taxPayerDetails.gst_number}`, form.value);
        const postNew = this.http.post(`${ApiUrls.taxPayerDefault}`, form.value)
        const apiUrl = !this.apiMethod ? postNew : updateGstNum;
        apiUrl.subscribe((res: any) => {
          try {
            if (res.data) {
              let dataObj = {
                // ...form.value,
                gst_number: form.value.gst_number,
                legal_name: form.value.legal_name,
                trade_name: form.value.trade_name,
                state_code: form.value.state_code,
                address_1: form.value.address_1,
                address_2: form.value.address_2,
                location: form.value.location,
                pincode: form.value.pincode,
                invoice_type: "B2B",
                irn_generated: this.invoiceInfo?.irn_generated == 'Success' ? 'Pending' : this.invoiceInfo?.irn_generated,
                // irn_generated: this.invoiceInfo?.qr_generated === 'Error' ? this.invoiceInfo?.qr_generated === 'Zero Invoice' ? 'Zero Invoice' : 'Error' : 'Pending',
                ready_to_generate_irn: 'Yes',
                qr_generated: "Pending",
                b2c_qrimage: '',
                b2c_qrinvoice: '',
                change_gst_number: 'No',
                place_of_supply: this.invoiceInfo?.place_of_supply || this.companyDetails?.state_code,
                converted_from_b2c: this.checkConvertToB2B ? '' : 'Yes',
                converted_from_b2c_by: this.checkConvertToB2B ? '' : login?.full_name,
                converted_from_b2c_time: this.checkConvertToB2B ? '' : Moment(new Date()).format('YYYY-MM-DD h:mm:ss')
              }
              this.http.put(ApiUrls.invoices + '/' + this.invoiceInfo.name, dataObj).subscribe((res) => {
                this.modal.dismissAll();
                this.getInvoiceInfo();
              });
            }
          } catch (e) { console.log(e) }
        })
      }

    } else {
      form.form.markAllAsTouched();
    }
  }

  async fileType(title: string, returnFile = false) {
    this.pdfView = true;
    let qrPng;
    this.invoiceTitle = title;
    if (title == "Original Invoice") {
      // this.invoiceTitle = title;
      title = "Original Invoice"
      qrPng = '';
      this.previewFile = this.invoiceInfo?.invoice_file ? this.apiDomain + this.invoiceInfo?.invoice_file : '';
    }
    if (title == "Tax Invoice" && this.invoiceInfo.invoice_type == 'B2B') {
      qrPng = this.invoiceInfo.qr_code_image;
    }
    if (title == "Tax Invoice with Credits") {
      qrPng = this.invoiceInfo.credit_qr_code_image;
    }
    if (title == "Tax Invoice" && this.invoiceInfo.invoice_type == 'B2C') {
      qrPng = this.invoiceInfo.b2c_qrimage;
    }
    // this.previewFile = type
    let xyz = this.apiDomain + this.invoiceInfo?.invoice_file;
    const existingPdfBytes = await fetch(xyz).then(res => res.arrayBuffer())
    const pdfDoc = await PDFDocument.load(existingPdfBytes, { ignoreEncryption: true });
    pdfDoc.setTitle(title);
    const pages = pdfDoc.getPages();
    const firstPage = this.companyDetails?.qr_page == 'Last' ? pages[pages.length - 1] : pages[0];
    let sampleImg = qrPng ? this.apiDomain + qrPng : null;
    // if (this.invoiceInfo?.signature) {
    //   // let sign = this.apiDomain+this.invoiceInfo?.signature_file;       
    //   const imgBytes2 = await this.http.get(this.invoiceInfo?.signature, { responseType: 'arraybuffer' }).toPromise();
    //   const signImage = await pdfDoc.embedPng(imgBytes2);
    //   const jpgDims = signImage.scale(0.5)
    //   console.log("signImage ====== ", signImage, signImage.height)
    //   pages[pages.length - 1].drawImage(signImage, {
    //     // x: 470,
    //     // y: 10,
    //     // width: 130,
    //     // height: 110
    //     // x: parseInt(this.invoiceInfo?.x1) - parseInt(this.invoiceInfo?.x0),
    //     // y: parseInt(this.invoiceInfo?.bottom) - parseInt(this.invoiceInfo?.top),
    //     x: parseInt(this.invoiceInfo?.x0),
    //     y: parseInt(this.invoiceInfo?.x1),
    //     width: 130, //parseInt(this.invoiceInfo?.x1)- parseInt(this.invoiceInfo?.x0), //130,
    //     height: 110 // parseInt(this.invoiceInfo?.bottom)-parseInt(this.invoiceInfo?.top) //110
    //   })
    // }
    if (sampleImg) {
      const imgBytes = await this.http.get(sampleImg, { responseType: 'arraybuffer' }).toPromise();
      const pngImage = await pdfDoc.embedPng(imgBytes);
      const pngDims = pngImage.scale(0.6);

      let x0, y0, x1, y1
      if (this.invoiceInfo?.pos_checks && this.invoiceInfo.invoice_type == "B2C" && this.companyDetails.pos_qr) {
        x0 = this.companyDetails.qr_b2c_rect_x0
        y0 = this.companyDetails.qr_b2c_rect_y0
        x1 = this.companyDetails.qr_b2c_rect_x1
        y1 = this.companyDetails.qr_b2c_rect_y1
      } else if (this.invoiceInfo?.pos_checks && this.invoiceInfo.invoice_type == "B2B" && this.companyDetails.pos_qr) {
        x0 = this.companyDetails.qr_b2b_rect_x0
        y0 = this.companyDetails.qr_b2b_rect_y0
        x1 = this.companyDetails.qr_b2b_rect_x1
        y1 = this.companyDetails.qr_b2b_rect_y1
      } else {
        x0 = this.companyDetails.qr_rect_x0
        y0 = this.companyDetails.qr_rect_y0
        x1 = this.companyDetails.qr_rect_x1
        y1 = this.companyDetails.qr_rect_y1
      }
      firstPage.drawImage(pngImage, {
        x: parseInt(x0),
        y: firstPage.getHeight() - parseInt(y0) - parseInt(y1),
        width: parseInt(x1),
        height: parseInt(y1)
      });

      if (this.invoiceInfo?.invoice_type == 'B2B') {
        if (this.companyDetails.irn_text_alignment === "Horizontal") {
          const page = this.companyDetails.irn_details_page === 'Last' ? pages[pages.length - 1] : pages[0];

          page.drawText(`IRN : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_irn_number : this.invoiceInfo?.irn_number}    ACK : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_ack_no : this.invoiceInfo?.ack_no}    Date : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_ack_date : this.invoiceInfo?.ack_date}`, {
            x: this.companyDetails?.irn_text_point1,
            y: page.getHeight() - parseInt(this.companyDetails.irn_text_point2),
            size: 8
          });

        } else {
          const page = this.companyDetails.irn_details_page === 'Last' ? pages[pages.length - 1] : pages[0];

          page.drawText(`IRN : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_irn_number : this.invoiceInfo?.irn_number}    ACK : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_ack_no : this.invoiceInfo?.ack_no}    Date : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_ack_date : this.invoiceInfo?.ack_date}    GSTIN : ${this.invoiceInfo?.gst_number}`, {
            x: this.companyDetails?.irn_text_point1,
            y: page.getHeight() - parseInt(this.companyDetails.irn_text_point2),
            rotate: degrees(90),
            size: 8
          });

        }

      }
      const pdfDataUri = await pdfDoc.saveAsBase64({ dataUri: true, addDefaultPage: true });
      this.previewFile = pdfDataUri;

      if (returnFile) {
        return await pdfDoc.save();
      }
      // console.log("Preview File",this.previewFile)
    } else {
      console.log('QR img not found');

    }
    const pdfDataUri = await pdfDoc.saveAsBase64({ dataUri: true, addDefaultPage: true });
    this.previewFile = pdfDataUri;

    if (returnFile) {
      return await pdfDoc.save();
    }
  }

  taxInvoice(type) {
    this.invoiceTitle = type;
    this.TaxInvoice = true;
    this.CreditInvoice = false;
    this.pdfView = false;
    this.http.post(ApiUrls.customEmailTemplates, {}).subscribe((res: any) => {
      if (res) {
      }
    })
  }

  creditInvoice(type) {
    this.invoiceTitle = type;
    this.CreditInvoice = true;
    this.TaxInvoice = false;
    this.pdfView = false;
    this.http.post(ApiUrls.customEmailTemplates, {}).subscribe((res: any) => {
      if (res) {
      }
    })
  }

  reAttachInvoice(): void {

    this.http.post(ApiUrls.reAttach, { invoice_number: this.invoiceInfo.invoice_number }).subscribe((res: any) => {
      if (res.message.success) {
        this.toastr.success(res.message.message);
        window.location.reload()
        this.getInvoiceInfo();
      } else {
        this.toastr.error(res.message.message)
      }
    })
  }


  editSacItem(item) {
    const queryParams: any = { filters: [['sac_index', '=', `${item.sac_index}`]] };
    queryParams.filters = JSON.stringify(queryParams.filters);
    this.http.get(`${ApiUrls.sacHsn}`, { params: queryParams }).subscribe((res: any) => {
      if (res?.data.length > 0) {
        this.http.get(`${ApiUrls.sacHsn}/${res.data[0].name}`).subscribe((res: any) => {
          if (res.data) {
            const editSacCode = this.modal.open(SacHsnComponent, {
              size: 'lg',
              centered: true,
              windowClass: 'modal-sac',
              animation: false
            })
            editSacCode.componentInstance.editSacHsn = res.data;
            editSacCode.result.then((res: any) => {
              if (res) {
                this.reload(this.invoiceInfo?.invoice_file)
              }
            }, (reason) => {
              console.log(reason);
            })
          }
        })
      } else {
        this.toastr.error("No SAC/HSN found")
      }
    })
  }

  editTempSacItem(item, index) {
    const tempEditITem = this.modal.open(TempSacLineComponent, {
      size: 'md',
      centered: true,
      windowClass: 'modal-sac',
      animation: false
    })
    this.checkSplit = false;
    tempEditITem.componentInstance.editLineItem = item;
    tempEditITem.result.then((res: any) => {
      if (res) {
        this.invoiceInfo.items[index].igst = res?.igst_value;
        this.invoiceInfo.items[index].sgst = res?.sgst_value;
        this.invoiceInfo.items[index].cgst = res?.cgst_value;
        this.invoiceInfo.items[index].vat = res?.vat_value;
        this.invoiceInfo.items[index].state_cess = res?.state_cess_value;
        this.invoiceInfo.items[index].cess = res?.cess_value;
        this.invoiceInfo.items[index].quantity = res?.quantity_value;
        this.invoiceInfo.items[index].discount_value = res?.discount_value_value;
        this.invoiceInfo.items[index].sc_gst_tax_rate = res?.sc_gst_tax_rate_value;
        this.invoiceInfo.items[index].sc_sac_code = res?.sc_sac_code_value;
        this.invoiceInfo.items[index].service_charge_rate = res?.service_charge_rate_value;
        this.invoiceInfo.items[index].net = res?.net;
        this.invoiceInfo.items[index].service_charge_tax_applies = res?.service_charge_tax_applies;


        this.tempLineItemEditApi()
      }
    })
  }
  typeOf(value) {
    return value % 1 != 0
  }

  switchSEZ() {
    if (this.sez == false || this.lut == false) {
      if (this.sez == false) {
        this.lut = false
      }
      console.log(this.invoiceInfo.items)
      this.invoiceInfo.items.forEach((res) => {
        res.lut_exempted = 0
      })
    }
    let manualEditObj = {
      data: {
        guest_data: {
          name: this.invoiceInfo?.guest_name,
          invoice_number: this.invoiceInfo?.invoice_number,
          invoice_date: this.invoiceInfo?.invoice_date,
          invoice_type: this.invoiceInfo?.invoice_type,
          gstNumber: this.invoiceInfo?.gst_number,
          room_number: this.invoiceInfo?.room_number,
          company_code: this.invoiceInfo?.company,
          confirmation_number: this.invoiceInfo?.confirmation_number,
          print_by: this.invoiceInfo?.print_by,
          invoice_file: this.invoiceInfo?.invoice_file
        },
        company_code: this.invoiceInfo?.company,
        items_data: this.invoiceInfo.items,
        total_inovice_amount: this.invoiceInfo?.total_invoice_amount,
        invoice_number: this.invoiceInfo?.invoice_number,
        taxpayer: {
          legal_name: this.invoiceInfo?.legal_name,
          address_1: this.invoiceInfo?.address_1,
          address_2: this.invoiceInfo?.address_2,
          email: this.invoiceInfo?.email,
          trade_name: this.invoiceInfo?.trade_name,
          phone_number: this.invoiceInfo?.phone_number,
          location: this.invoiceInfo?.location,
          pincode: this.invoiceInfo?.pincode,
          state_code: this.invoiceInfo?.state_code
        },
        sez: this.sez == true ? 1 : 0,
        lut: this.lut == true ? 1 : 0,
      }
    }
    console.log(manualEditObj)
    this.http.post(ApiUrls.tempLineItemEdit, manualEditObj).subscribe((res: any) => {
      if (res?.message?.success) {
        this.isChecked = false
        this.getInvoiceInfo();
      }
    })
  }

  isAllSelected(item) {

    this.http.post(`${ApiUrls.resource}/${Doctypes.items}/${item.name}`, { 'lut_exempted': item.lut_exempted ? 1 : 0 }).subscribe((res: any) => {
      if (res?.message?.success) {
        this.getInvoiceInfo();
      }


    })
  }


  openInvoice() {
    this.irnObject = {}
    this.fileType('Original Invoice');
    this.modal.open(this.invoicePdf, {
      size: 'lg',
      centered: true,
      windowClass: 'sideMenuPdf',
    });
    if (this.invoiceInfo?.irn_generated == "Pending" && this.invoiceInfo?.invoice_type == "B2B") {
      this.getIrnObjectPending();
    }
    if (this.invoiceInfo?.irn_generated == "Success" && this.invoiceInfo?.invoice_type == "B2B") {
      this.getIrnObjectSuccess();
    }
  }

  getIrnObjectSuccess() {
    const queryParams: any = { filters: [['invoice_number', '=', `${this.invoiceInfo.invoice_number}`], ['irn_status', '=', 'Success']] };
    queryParams.fields = JSON.stringify(["name", "invoice_number", "irn_request_object", "invoice_category", "irn_response_object", "allowance_irn_request_object", "allowance_irn_response_object"]);
    queryParams.filters = JSON.stringify(queryParams.filters);
    this.http.get(`${ApiUrls.resource}/${Doctypes.irnObj}`, { params: queryParams }).subscribe((res: any) => {
      if (res.data) {
        let irnObj = {}
        irnObj['irn_request_object'] = JSON.parse(res.data[0]?.irn_request_object)
        irnObj['irn_response_object'] = JSON.parse(res.data[0]?.irn_response_object)
        if (res.data[0]?.allowance_irn_request_object) {
          irnObj['allowance_irn_request_object'] = JSON.parse(res.data[0]?.allowance_irn_request_object)
        }
        if (res.data[0]?.allowance_irn_response_object) {
          irnObj['allowance_irn_response_object'] = JSON.parse(res.data[0]?.allowance_irn_response_object)
        }
        this.irnObject = irnObj;
        console.log(this.irnObject)
      }
    })
  }
  getIrnObjectPending() {
    this.http.post(ApiUrls.pendingIrnObj, { invoice_number: this.invoiceInfo?.invoice_number }).subscribe((res: any) => {
      if (res?.message?.success) {
        this.irnObject = res?.message?.data
      }
    })
  }
  InvoicePdf(type) {
    this.invoicetypeName = type
    if (type === "tax") {
      this.invoicetype = true;
    }
    if (type === "credit") {
      this.invoicetype = false;
    }
  }

  // ConvertB2BTOB2C

  ConvertB2BTOB2C() {
    let dataObj = {
      gst_number: '',
      legal_name: '',
      trade_name: '',
      state_code: '',
      address_1: '',
      address_2: '',
      location: '',
      pincode: '',
      invoice_type: "B2C",
      irn_generated: this.invoiceInfo?.irn_generated == 'Success' ? 'Pending' : this.invoiceInfo?.irn_generated,
      ready_to_generate_irn: 'Yes',
      // qr_generated: "Pending",
      // b2c_qrimage: '',
      // b2c_qrinvoice: '',
      converted_from_b2b: 'Yes',
      converted_from_b2b_by: this.loginData?.full_name,
      converted_from_b2b_time: Moment(new Date()).format('YYYY-MM-DD h:mm:ss'),
      change_gst_number: 'No'
    }
    this.http.put(ApiUrls.invoices + '/' + this.invoiceInfo.name, dataObj).subscribe((res: any) => {
      // console.log(res)
      if (res.data) {
        this.getInvoiceInfo();
      }

    });

  }
  deleteItems(event, item) {
    if (item.checked) {
      item.checked = !item.checked;
    } else {
      item['checked'] = true;
      this.isChecked = true;
    }
    this.dupItems = [this.invoiceInfo]
    this.dupItems = this.dupItems[0]?.items.filter((each: any) => each.checked)
    if (this.dupItems.length) {
      this.isChecked = true;
    } else {
      this.isChecked = false;
    }
  }

  deleteLineItems() {
    this.dupItems = { ...this.invoiceInfo }
    this.dupItems = this.dupItems?.items.filter((each: any) => !each.checked)
    let formatDate = Moment(this.invoiceInfo.invoice_date).format('DD-MMM-YY h:mm:ss')
    const todayDate = Moment().format('YYYY-MM-DD h:mm:ss');
    const data = this.invoiceInfo
    this.invoiceInfo['items'] = this.dupItems;
    this.invoiceInfo['items_data'] = this.dupItems;
    this.invoiceInfo['company_code'] = this.companyDetails.company_code;
    this.invoiceInfo['total_invoice_amount'] = this.invoiceInfo.total_invoice_amount;
    this.invoiceInfo['invoice_number'] = this.invoiceInfo.invoice_number;
    this.invoiceInfo['amened'] = 'No';
    // this.invoiceInfo['invoice_from'] = 'Web';
    this.invoiceInfo['guest_data'] = {
      address1: this.invoiceInfo.address1,
      invoice_type: this.invoiceInfo.invoice_type,
      invoice_category: 'Tax Invoice',
      invoice_number: this.invoiceInfo.invoice_number,
      name: this.invoiceInfo.guest_name,
      gstNumber: this.invoiceInfo.gst_number,
      invoice_file: this.invoiceInfo.invoice_file,
      room_number: this.invoiceInfo.room_number,
      invoice_date: formatDate,
      confirmation_number: 0,
      print_by: this.companyDetails.company_code,
      membership: 0,
      start_time: todayDate,
      items: this.dupItems

    };
    this.invoiceInfo['taxpayer'] = {
      guest_name: this.invoiceInfo.guest_name,
      gst_number: this.invoiceInfo.gst_number,
      legal_name: this.invoiceInfo.legal_name,
      trade_name: this.invoiceInfo.trade_name,
      address_1: this.invoiceInfo.address_1,
      address_2: this.invoiceInfo.address_2,
      state_code: this.invoiceInfo.state_code,
      location: this.invoiceInfo.location,
      pincode: this.invoiceInfo.pincode,
      email: '',
      phone_number: '',
    };
    this.http.post(ApiUrls.sac_items, {
      "data": data
    }).subscribe((res: any) => {
      if (res.message.success) {
        this.toastr.success('Successfully Deleted');
        this.getInvoiceInfo();
        this.isChecked = false;
      } else {
        this.toastr.error('Error');
      }
    })
  }

  printPdf() {
    let head: any = document.getElementsByClassName('invoice-details')[0]
    let style: any = document.createElement('style');
    if (this.companyDetails.e_tax_format == 'Landscape') {
      let css = '@page { size: landscape; }'
      style.type = 'text/css';
      style.media = 'print';

      if (style.styleSheet) {
        style.styleSheet.cssText = css;
      } else {
        style.appendChild(document.createTextNode(css));
      }

      head.appendChild(style);
      console.log(head.getElementsByTagName('style'))
    } else {
      console.log(head.getElementsByTagName('style'))
      let innerStyleTags = head.getElementsByTagName('style')
      if (innerStyleTags.length) {
        head.removeChild(innerStyleTags[0])
      }
    }

    this.printEnable = true;
    window.print();

  }

  /**Split Line items */
  // editSplitItemSac(item,index){
  //   let modalObj = this.modal.open(SplitLineItemsSacComponent, {
  //     size: 'lg',
  //     centered: true,
  //     windowClass: 'modal-sac',
  //     animation: false
  //   })
  //   modalObj.componentInstance.editLineItemData = item;
  // }

  // editSplitItem(item, index) {
  //   let modalObj = this.modal.open(SplitLineItemsComponent, {
  //     size: 'md',
  //     centered: true,
  //     windowClass: 'modal-sac',
  //     animation: false
  //   })

  // editSplitItemSac(item, index) {
  //   let modalObj = this.modal.open(SplitLineItemsSacComponent, {
  //     size: 'lg',
  //     centered: true,
  //     windowClass: 'modal-sac',
  //     animation: false
  //   })
  //   modalObj.componentInstance.editLineItemData = item;
  //   modalObj.result.then((res: any) => {
  //     console.log(res)
  //     this.checkSplit = true
  //     // let dupArrayList = [];
  //     if (res) {

  //       const maxValueOfSort = Math.max(...this.invoiceInfo.items.map(o => o.sort_order), 0);

  //       let SplitObj = {};
  //       SplitObj['item_value'] = JSON.parse(res?.splitValue);
  //       SplitObj['igst'] = res?.igst_value;
  //       SplitObj['sgst'] = res?.sgst_value;
  //       SplitObj['cgst'] = res?.cgst_value;
  //       SplitObj['vat'] = res?.vat_value;
  //       SplitObj['state_cess'] = res?.state_cess_value;
  //       SplitObj['cess'] = res?.cess_value;
  //       SplitObj['quantity'] = res?.quantity_value;
  //       SplitObj['discount_value'] = res?.discount_value_value;
  //       SplitObj['sc_gst_tax_rate'] = res?.sc_gst_tax_rate_value;
  //       // SplitObj['sc_sac_code'] = res?.sc_sac_code_value;
  //       SplitObj['service_charge_rate'] = res?.service_charge_rate_value;
  //       SplitObj['service_chargeEdit'] = res?.service_chargeEdit;
  //       SplitObj['is_service_charge_item'] = "No";
  //       SplitObj['unit_of_measurement_description'] = this.invoiceInfo.items[index].unit_of_measurement_description;
  //       SplitObj['unit_of_measurement'] = this.invoiceInfo.items[index].unit_of_measurement;
  //       SplitObj['net'] = res?.net;
  //       SplitObj['service_charge_tax_applies'] = res?.service_charge_tax_applies;
  //       SplitObj['date'] = this.invoiceInfo.items[index].date;
  //       SplitObj['description'] = res?.description;
  //       SplitObj['doctype'] = this.invoiceInfo.items[index].doctype;
  //       SplitObj['name'] = res?.description;
  //       SplitObj['sac_index'] = this.invoiceInfo.items[index].sac_index;
  //       SplitObj['sort_order'] = Math.round(maxValueOfSort) + 1;
  //       SplitObj['item_name'] = res?.description;
  //       SplitObj['sac_code'] = res.sac_code;
  //       SplitObj['is_manual_edit'] = 'No';
  //       SplitObj['manual_edit'] = 'Yes';
  //       SplitObj['sc_gst_tax_rate'] = res?.sc_gst_tax_rate;
  //       SplitObj['sc_sac_code'] = res?.sc_sac_code;


  //       this.dupArrayList = [...this.invoiceInfo?.items];
  //       this.dupArrayList.push(SplitObj);
  //       if (res.splitValue) {
  //         this.dupArrayList[index].item_value = (this.dupArrayList[index].item_value) - (res?.splitValue);
  //         this.dupArrayList[index]['is_manual_edit'] = true;
  //         this.dupArrayList[index].discount_value = 0;
  //         this.dupArrayList[index].service_charge_rate = this.invoiceInfo?.items[index].service_charge_rate_value;
  //         this.dupArrayList[index]['manual_edit'] = "Yes";
  //         this.dupArrayList[index]['sc_gst_tax_rate'] = this.invoiceInfo?.items[index].sc_gst_tax_rate_value;
  //         this.dupArrayList[index]['sc_sac_code'] = this.invoiceInfo?.items[index].sac_code;

  //         // this.invoiceInfo.items[index].item_value = (this.invoiceInfo.items[index].item_value) - (res?.splitValue);
  //         // this.invoiceInfo.items[index]['is_manual_edit'] = true;
  //         // this.invoiceInfo.items[index].discount_value = 0;
  //         // this.invoiceInfo.items[index].service_charge_rate = this.invoiceInfo?.items[index].service_charge_rate;
  //         // this.invoiceInfo.items[index]['manual_edit'] = "Yes";
  //       }

  //       this.tempLineItemEditApi()
  //     }
  //     // console.log(this.invoiceInfo.items,this.invoiceInfo?.items[index].service_charge_rate,res.service_charge_rate_value)
  //     // return res


  //   })
  // }

  tempLineItemEditApi() {

    let manualEditObj = {
      data: {
        guest_data: {
          name: this.invoiceInfo?.guest_name,
          invoice_number: this.invoiceInfo?.invoice_number,
          invoice_date: this.invoiceInfo?.invoice_date,
          invoice_type: this.invoiceInfo?.invoice_type,
          gstNumber: this.invoiceInfo?.gst_number,
          room_number: this.invoiceInfo?.room_number,
          company_code: this.invoiceInfo?.company,
          confirmation_number: this.invoiceInfo?.confirmation_number,
          print_by: this.invoiceInfo?.print_by,
          invoice_file: this.invoiceInfo?.invoice_file
        },
        company_code: this.invoiceInfo?.company,
        items_data: this.invoiceInfo?.items,
        total_inovice_amount: this.invoiceInfo?.total_invoice_amount,
        invoice_number: this.invoiceInfo?.invoice_number,
        taxpayer: {
          legal_name: this.invoiceInfo?.legal_name,
          address_1: this.invoiceInfo?.address_1,
          address_2: this.invoiceInfo?.address_2,
          email: this.invoiceInfo?.email,
          trade_name: this.invoiceInfo?.trade_name,
          phone_number: this.invoiceInfo?.phone_number,
          location: this.invoiceInfo?.location,
          pincode: this.invoiceInfo?.pincode,
          state_code: this.invoiceInfo?.state_code
        },
        sez: this.sez === true ? 1 : 0
      }
    }
    console.log(manualEditObj)
    this.http.post(ApiUrls.tempLineItemEdit, manualEditObj).subscribe((res: any) => {
      if (res?.message?.success) {

        this.getInvoiceInfo();
      }
    })
  }

  /**convert to Credit Note */
  convertCredit(moveToCreditDateEdit) {
    let modal = this.modal.open(moveToCreditDateEdit, { size: 'md', centered: true })
    // const dataObj = {
    //   invoice_category: 'Credit Invoice'
    // }
    // this.http.put(`${ApiUrls.invoices}/${this.invoiceInfo.invoice_number}`, dataObj).subscribe((res: any) => {
    //   if (res.data) {
    //     this.toastr.success("This invoice moved to credit notes")
    //     this.route.navigate(['/home/invoices'])

    //   }
    // })
  }
  updateInvoiceDateNumber(form: NgForm, modal) {
    if (form.valid) {
      let dataObj;
      if (this.invoiceInfo?.invoice_type == "B2C" && this.invoiceInfo.irn_generated === 'Error') {
        dataObj = {
          invoice_category: 'Credit Invoice',
          invoice_round_off_amount: 0,
          ...form.value
        }
      } else {
        dataObj = {
          invoice_category: 'Credit Invoice',
          ...form.value
        }
      }

      this.http.put(`${ApiUrls.invoices}/${this.invoiceInfo.invoice_number}`, dataObj).subscribe((res: any) => {
        if (res.data) {
          this.toastr.success("This invoice moved to credit notes")
          modal.close();
          this.route.navigate(['/home/invoices'])

        }
      })
    }

  }

  /**Convert to Debit */
  convertDebit() {
    const dataObj = {
      invoice_category: 'Debit Invoice'
    }
    this.http.put(`${ApiUrls.invoices}/${this.invoiceInfo.invoice_number}`, dataObj).subscribe((res: any) => {
      if (res.data) {
        this.toastr.success("This invoice moved to Debit notes")
        this.route.navigate(['/home/invoices'])

      }
    })
  }
  /**Delete Invoice */
  deleteInvoices() {
    if (!window.confirm(`Are you sure to delete Invoice? `)) {
      return null;
    } else {
      this.http.delete(`${ApiUrls.invoices}/${this.invoiceInfo?.name}`).subscribe((res: any) => {
        if (res?.message == 'ok') {
          this.toastr.success("This invoice is deleted")
          this.route.navigate(['/home/invoices'])
        }
      })
    }
  }

  // update invoice Address 1
  editAddress1fun(editAddress1) {
    let modal = this.modal.open(editAddress1, { centered: true, size: 'md' })
    this.address1_state = this.invoiceInfo?.address_1
  }
  // update invoice Address 1
  editAddress2fun(editAddress2) {
    let modal = this.modal.open(editAddress2, { centered: true, size: 'md' })
    this.address2_state = this.invoiceInfo?.address_2
  }
  // update invoice location
  locationfun(invoiceLocation) {
    let modal = this.modal.open(invoiceLocation, { centered: true, size: 'md' })
    this.location_state = this.invoiceInfo?.location
  }
  /**updateInvoice place of Supply */

  editPOS(editPlaceOfSupply) {
    let modal = this.modal.open(editPlaceOfSupply, { centered: true, size: 'md' })
    this.place_of_supply_state = this.invoiceInfo?.place_of_supply_name?.state
  }

  modelChangeFn(e) {
    this.place_of_supply = e.tin
  }
  updateInvoicePOS(form: NgForm, modalRef) {
    if (form.valid) {
      this.http.put(ApiUrls.invoices + '/' + this.invoiceInfo.name, { place_of_supply: form.value?.place_of_supply?.tin }).subscribe((res) => {
        modalRef.close();
        this.tempLineItemEditApi();
        this.toastr.success("Tax Payer Details updated")
        // this.reload(this.invoiceInfo?.invoice_file)
      });
    } else {
      form.form.markAllAsTouched();
    }
  }

  // updating invoice address1
  updateInvoiceAddress1(form: NgForm, modalRef) {
    if (form.valid) {
      this.http.put(ApiUrls.invoices + '/' + this.invoiceInfo.name, { address_1: form.value?.address1 }).subscribe((res) => {
        modalRef.close();
        this.getInvoiceInfo();
        this.toastr.success("Tax Payer Details updated")
        // this.tempLineItemEditApi();
        // this.reload(this.invoiceInfo?.invoice_file)
      });
    } else {
      form.form.markAllAsTouched();
    }
  }

  // updating invoice address2
  updateInvoiceAddress2(form: NgForm, modalRef) {
    if (form.valid) {
      this.http.put(ApiUrls.invoices + '/' + this.invoiceInfo.name, { address_2: form.value?.address2 }).subscribe((res) => {
        modalRef.close();
        this.getInvoiceInfo();
        this.toastr.success("Tax Payer Details updated")
        // this.tempLineItemEditApi();
        // this.reload(this.invoiceInfo?.invoice_file)
      });
    } else {
      form.form.markAllAsTouched();
    }
  }

  // updating invoice location
  updateInvoiceLocation(form: NgForm, modalRef) {
    if (form.valid) {

      this.http.put(ApiUrls.invoices + '/' + this.invoiceInfo.name, { location: form.value?.location }).subscribe((res) => {
        modalRef.close();
        this.getInvoiceInfo();
        this.http.put(ApiUrls.taxPayerDefault + '/' + this.invoiceInfo.gst_number, { location: form.value?.location }).toPromise();
        this.toastr.success("Tax Payer Details updated")
        // this.tempLineItemEditApi();
        // this.reload(this.invoiceInfo?.invoice_file)
      });
    } else {
      form.form.markAllAsTouched();
    }
  }
  /**addInvoiceItem for invoice */

  async addInvoiceItem() {
    this.addItemModelRef = "addItem"
    this.getCodesCount();
    this.creditInvoiceItem = {}
    this.creditInvoiceItem['invoice_date'] = this.invoiceInfo?.invoice_date
    this.sacDetails = ''
    this.uomData = UOMCode
    const modalRef = await this.modal.open(this.addInvoiceModal, {
      size: 'md',
      centered: true,
    });
    modalRef.result.finally(() => {
      this.sacCodeName = null;
      // this.sacDetails = null;
      this.checkITemType = null;
    });
  }

  async getCodesCount() {
    const res: any = await this.http.get(`${ApiUrls.sacHsn}`, {
      params: {
        fields: JSON.stringify(["count( `tabSAC HSN CODES`.`name`) AS total_count"])
      }
    }).toPromise().catch((err) => '');
    if (res) {
      this.totalCount = res.data[0].total_count;
      await this.getCodesData();
    }
  }

  async getCodesData() {
    let queryParams: any = { filters: [] }
    // if (this.sacCodeName) {
    queryParams.filters.push(['ignore', 'like', `0`]);
    // }

    queryParams.limit_start = 0
    queryParams.limit_page_length = this.totalCount;
    queryParams.order_by = "`tabSAC HSN CODES`.`creation` desc"
    queryParams.fields = JSON.stringify(["name", "net"]);
    queryParams.filters = JSON.stringify(queryParams.filters);

    // const countApi = this.http.get(`${ApiUrls.sacHsn}`, {
    //   params: {
    //     fields: JSON.stringify(["count( `tabSAC HSN CODES`.`name`) AS total_count"]),
    //     filters: queryParams.filters
    //   }
    // });
    const res: any = await this.http.get(`${ApiUrls.sacHsn}`, { params: queryParams }).toPromise().catch((err) => '');
    if (res) {
      this.sacCodeData = res.data;
    }

  }

  register(form, index) {
    if (form.invalid) {
      form.form.markAllAsTouched();
      return;
    }
    const maxValueOfSort = Math.max(...this.invoiceInfo.items.map(o => o.sort_order), 0);
    let uomCode = UOMCode.find((res: any) => res.description === form.value.unit_of_measurement_description)
    let string = this.companyDetails.invoice_item_date_format; // just an example
    string = string.replaceAll('%', '');
    string = string.replaceAll('d', 'DD');
    string = string.replaceAll('m', 'MM');
    string = string.replaceAll('b', 'MMM');
    string = string.replaceAll('Y', 'YYYY');
    string = string.replaceAll('y', 'YY');

    string = string.toUpperCase();
    this.date = Moment(form.value.invoice_date).format(string)
    console.log(this.date)
    // if (this.companyDetails.invoice_item_date_format == '%d-%m-%y') {
    //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD-MM-YY')
    // }

    // if (this.companyDetails.invoice_item_date_format == '%d/%m/%y') {
    //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD/MM/YY')
    // }
    // if (this.companyDetails.invoice_item_date_format == '%d/%m/%Y') {
    //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD/MM/YYYY')
    // }

    // if (this.companyDetails.invoice_item_date_format == '%d.%m.%y') {
    //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD.MM.YY')
    // }
    form.value['item_value'] = JSON.parse(form.value.split_value ? form.value.split_value : this.sacCodePrice);
    form.value['date'] = this.date;
    form.value['name'] = this.sacCodeName?.name ? this.sacCodeName?.name : this.creditInvoiceItem?.description;
    form.value['sac_code'] = 'No Sac';
    form.value['sort_order'] = Math.round(maxValueOfSort) + 1;;
    form.value['quantity'] = form.value.quantity || 1;
    form.value['unit_of_measurement_description'] = form.value.unit_of_measurement_description || 'OTHERS';
    form.value['unit_of_measurement'] = uomCode?.code || 'OTH';
    form.value['sez'] = this.invoiceInfo?.sez;
    form.value['invoice_number'] = this.invoiceInfo?.invoice_number;
    let temp = [];
    // let hadNet = false;
    if (this.sacCodeDetails[index]) {
      this.sacCodeDetails[index]['split_value'] = form.value.split_value;
    }
    for (let each of this.sacCodeDetails) {
      if (each.item_name) {
        each.name = each.item_name;
        each.date = Moment(each.date).format(string)
        // each.date = this.companyDetails.invoice_item_date_format === '%d-%m-%y' ?  Moment(each.date).format('DD-MM-YY') : Moment(each.date).format('DD/MM/YY');
      }
      temp.push(each);
      // if(each.name == this.sortedListInvoice[index].item_name && !hadNet){
      //   hadNet = each.net == "Yes";
      // }
    }
    // let temp = this.sacCodeDetails.map((each) => {
    //   if (each.item_name) {
    //     each.name = each.item_name;
    //     each.date = this.companyDetails.invoice_item_date_format === '%d-%m-%y' ? Moment(each.date).format('DD-MM-YY') : Moment(each.date).format('DD/MM/YY');
    //   }
    //   return each
    // });
    // temp = temp.filter((each: any) => each?.is_service_charge_item == 'No')
    // console.log('hadNet: ',hadNet);
    if (form.value?.split_value) {
      temp[index].item_value = this.creditInvoiceItem.value - (form.value.split_value);
    }
    // temp = temp.filter((each: any) => each?.is_service_charge_item == 'No')
    const data = {
      "data": {
        "items": [...temp, form.value],
        "place_of_supply": this.invoiceInfo?.place_of_supply,
        "company_code": this.companyDetails.company_code,
        "invoice_number": this.invoiceNumber,
        "invoice_item_date_format": this.companyDetails.invoice_item_date_format,
        "guest_data": {
          invoice_category: 'Tax Invoice'
        }
      }
    }
    if (data) {
      this.http.post(ApiUrls.cal_items, data).subscribe((res: any) => {
        if (res.message) {
          this.sacCodeDetails = [...res.message.data];
          this.sacCodeDetails = this.sacCodeDetails.sort((a, b) => parseFloat(a.sort_order) - parseFloat(b.sort_order))
          this.toastr.success('item created');
          this.modal.dismissAll(form.reset());
          this.saveItems()
        } else {
          this.toastr.error('Error');
          this.modal.dismissAll()
        }
      })
    }
  }

  saveItems() {
    let formatDate = Moment(this.invoiceInfo?.invoice_date).format('DD-MMM-YY h:mm:ss')
    const todayDate = Moment().format('YYYY-MM-DD h:mm:ss');
    console.log("============", this.companyDetails)
    this.invoiceInfo['items_data'] = this.sacCodeDetails
    this.invoiceInfo['company_code'] = this.companyDetails.company_code;
    this.invoiceInfo['total_invoice_amount'] = this.invoiceInfo.total_invoice_amount;
    this.invoiceInfo['invoice_number'] = this.invoiceInfo.invoice_number;
    this.invoiceInfo['amened'] = 'No';
    // this.invoiceInfo['invoice_from'] = 'Web';
    this.invoiceInfo['place_of_supply'] = this.invoiceInfo?.place_of_supply;
    this.invoiceInfo['guest_data'] = {
      address1: this.invoiceInfo.address1,
      invoice_type: this.invoiceInfo.invoice_type,
      invoice_category: 'Tax Invoice',
      invoice_number: this.invoiceInfo.invoice_number,
      name: this.invoiceInfo.guest_name,
      gstNumber: this.invoiceInfo.gst_number,
      invoice_file: this.invoiceInfo.invoice_file,
      room_number: this.invoiceInfo?.room_number || 0,
      invoice_date: formatDate,
      confirmation_number: this.invoiceInfo?.confirmation_number || 0,
      print_by: this.companyDetails.company_code,
      membership: 0,
      start_time: todayDate,
      items: this.sacCodeDetails

    };
    this.invoiceInfo['taxpayer'] = {
      guest_name: this.invoiceInfo.guest_name,
      gst_number: this.invoiceInfo.gst_number,
      legal_name: this.invoiceInfo.legal_name,
      trade_name: this.invoiceInfo.trade_name,
      address_1: this.invoiceInfo.address_1,
      address_2: this.invoiceInfo.address_2,
      state_code: this.invoiceInfo.state_code,
      location: this.invoiceInfo.location,
      pincode: this.invoiceInfo.pincode,
      email: '',
      phone_number: '',

    };
    const data = this.invoiceInfo;
    this.http.post(ApiUrls.sac_items, {
      "data": data
    }).subscribe((res: any) => {
      if (res.message.success) {
        this.sacCodeName = ''
        this.addItemModelRef = "";
        this.toastr.success('Successfully Created');
        // setTimeout((res: any) => {
        this.getInvoiceInfo();
        // }, 1000)

      } else {
        this.toastr.error('Error');
      }
    })
  }


  modelChangeSac(e, type) {
    // if (this.addItemModelRef == 'splitItem') {
    //   this.sacCodeName =  this.creditInvoiceItem?.description
    //   this.sacCodePrice = this.creditInvoiceItem?.split_value
    // }
    if (!e) {
      return;
    }
    if (type === 'name') {
      this.sacCodeName = e

      this.http.get(`${ApiUrls.sacHsn}/${e.name}`).subscribe((res: any) => {

        if (res) {
          this.checkITemType = res.data.type;
          this.creditInvoiceItem.quantity = this.checkITemType == 'HSN' ? 1 : this.companyDetails.company_code === this.hindia_prop ? 1 : null;
          this.creditInvoiceItem.unit_of_measurement_description = this.checkITemType == 'HSN' ? 'UNITS' : this.companyDetails.company_code === this.hindia_prop ? 'OTHERS' : null;
        }
      })

    }

    if (type === 'price') {
      this.sacCodePrice = e
    }
    // let InclTax=0;
    // if(type === 'tax'){
    //   InclTax = e
    // }
    if (this.sacCodeName && this.sacCodePrice) {
      if (this.addItemModelRef == 'splitItem') {
        if (!this.creditInvoiceItem.net) {
          return;
        }
      }
      let string = this.companyDetails.invoice_item_date_format; // just an example
      string = string.replaceAll('%', '');
      string = string.replaceAll('d', 'DD');
      string = string.replaceAll('m', 'MM');
      string = string.replaceAll('b', 'MMM');
      string = string.replaceAll('Y', 'YYYY');
      string = string.replaceAll('y', 'YY');

      string = string.toUpperCase();
      this.date = Moment(this.invoiceInfo.invoice_date).format(string)
      // if (this.companyDetails.invoice_item_date_format == '%d-%m-%y') {
      //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD-MM-YY')
      // }

      // if (this.companyDetails.invoice_item_date_format == '%d/%m/%y') {
      //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD/MM/YY')
      // }
      // if (this.companyDetails.invoice_item_date_format == '%d/%m/%Y') {
      //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD/MM/YYYY')
      // }

      // if (this.companyDetails.invoice_item_date_format == '%d.%m.%y') {
      //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD.MM.YY')
      // }
      // console.log("date ===", this.date, this.sacCodeName)
      // const dateformat = date.getDate() + '-' + (date.getMonth() + 1) + '-' + (date.getFullYear().toString().substr(-2));
      const form = {
        "item_value": JSON.parse(this.sacCodePrice),
        "date": this.date,
        "name": this.sacCodeName?.name ? this.sacCodeName?.name : this.creditInvoiceItem?.description,
        "sac_code": 'No Sac',
        "sort_order": this.sort_order + 1,
        "net": this.creditInvoiceItem.net
        // "inclTax" : InclTax
      }
      const data = {
        "data": {
          "items": [form],
          "company_code": this.companyDetails.company_code,
          "invoice_number": this.invoiceNumber,
          "place_of_supply": this.invoiceInfo?.place_of_supply,
          "invoice_item_date_format": this.companyDetails.invoice_item_date_format,
          "guest_data": {
            invoice_category: 'Tax Invoice'
          }
        }
      }
      if (data) {
        this.http.post(ApiUrls.cal_items, data).subscribe((res: any) => {
          if (res.message) {
            const sacCodes = res.message.data;
            this.sacDetails = res.message.data[0]
            this.checkSplitAmount = false;
          }
        })
      }
    }


  }

  modelChangeSacQuantity(e, type, totlaAmt) {
    // if (this.addItemModelRef == 'splitItem') {
    //   this.sacCodeName =  this.creditInvoiceItem?.description
    //   this.sacCodePrice = this.creditInvoiceItem?.split_value
    // }
    if (!e) {
      return;
    }

    if (type === 'price') {
      // this.sacCodePrice = e
      this.sacCodePrice = totlaAmt

    }
    // let InclTax=0;
    // if(type === 'tax'){
    //   InclTax = e
    // }
    if (this.sacCodeName && this.sacCodePrice) {
      if (this.addItemModelRef == 'splitItem') {
        if (!this.creditInvoiceItem.net) {
          return;
        }
      }
      let string = this.companyDetails.invoice_item_date_format; // just an example
      string = string.replaceAll('%', '');
      string = string.replaceAll('d', 'DD');
      string = string.replaceAll('m', 'MM');
      string = string.replaceAll('b', 'MMM');
      string = string.replaceAll('Y', 'YYYY');
      string = string.replaceAll('y', 'YY');

      string = string.toUpperCase();
      this.date = Moment(this.invoiceInfo.invoice_date).format(string)
      // if (this.companyDetails.invoice_item_date_format == '%d-%m-%y') {
      //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD-MM-YY')
      // }

      // if (this.companyDetails.invoice_item_date_format == '%d/%m/%y') {
      //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD/MM/YY')
      // }
      // if (this.companyDetails.invoice_item_date_format == '%d/%m/%Y') {
      //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD/MM/YYYY')
      // }

      // if (this.companyDetails.invoice_item_date_format == '%d.%m.%y') {
      //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD.MM.YY')
      // }
      // console.log("date ===", this.date, this.sacCodeName)
      // const dateformat = date.getDate() + '-' + (date.getMonth() + 1) + '-' + (date.getFullYear().toString().substr(-2));
      const form = {
        "item_value": JSON.parse(this.sacCodePrice),
        "date": this.date,
        "name": this.sacCodeName?.name ? this.sacCodeName?.name : this.creditInvoiceItem?.description,
        "sac_code": 'No Sac',
        "sort_order": this.sort_order + 1,
        "net": this.creditInvoiceItem.net
        // "inclTax" : InclTax
      }
      const data = {
        "data": {
          "items": [form],
          "company_code": this.companyDetails.company_code,
          "invoice_number": this.invoiceNumber,
          "place_of_supply": this.invoiceInfo?.place_of_supply,
          "invoice_item_date_format": this.companyDetails.invoice_item_date_format,
          "guest_data": {
            invoice_category: 'Tax Invoice'
          }
        }
      }
      console.log(data)
      if (data) {
        this.http.post(ApiUrls.cal_items, data).subscribe((res: any) => {
          if (res.message) {
            const sacCodes = res.message.data;
            this.sacDetails = res.message.data[0]
            this.checkSplitAmount = false;
          }
        })
      }
    }


  }

  /**Split Line Item Changes*/
  async splitLineItemModel(item, index) {
    this.addItemModelRef = "splitItem";
    await this.getCodesCount();
    let hadNet = false;

    for (let each of this.sacCodeData) {
      if (each.name == item.item_name && !hadNet) {
        hadNet = each.net == "Yes";
        break;
      }
    }
    this.creditInvoiceItem = { ...item };
    this.creditInvoiceItem.hadNet = hadNet;
    let netSCamount;

    if (hadNet) {
      let sortNumber = this.invoiceInfo?.items.find((res: any) => (this.creditInvoiceItem.sort_order + 0.1) == res.sort_order)
      //  console.log("sort=====",sortNumber)
      this.creditInvoiceItem.value = this.creditInvoiceItem.item_value_after_gst + sortNumber?.item_value_after_gst;
    } else {
      this.creditInvoiceItem.value = hadNet ? this.creditInvoiceItem.item_value_after_gst : this.creditInvoiceItem.item_value;
    }
    this.sacDetails = '';
    this.sacCodeName = { name: item?.item_name };
    this.creditInvoiceItem.split_value = null;
    this.creditInvoiceItem.net = 'No';
    const modalRef = this.modal.open(this.addInvoiceModal, {
      size: 'md',
      centered: true,
    });
    modalRef.result.then((res: any) => {
      this.checkITemType = null;
      this.addItemModelRef = "";
      this.register(res, index)
    })
  }


  /**convert To Manual Invoice */
  convertManual() {
    if (!window.confirm(`Are you sure to move Manual Invoice for Invoice ${this.invoiceInfo.name} ?`)) {
      return null;
    } else {
      let dataObj = {
        converted_from_tax_invoices_to_manual_tax_invoices: "Yes",
        irn_generated: "Pending",
        invoice_from: 'Web',
        error_message: '',
        ready_to_generate_irn: 'Yes',
        invoice_round_off_amount: 0
      }
      this.http.put(`${ApiUrls.invoices}/${this.invoiceInfo.name}`, dataObj).subscribe((res: any) => {
        if (res?.data) {
          this.toastr.success("Moved to Manual Tax Invoices")
          this.location.back();
        } else {
          this.toastr.error("")
        }
      })
    }
  }

  /**Convert invoice to Credit Note Manual */
  convertCreditMAnual(SuccessInvoiceChanges) {
    this.changeInvoiceForm = { ...this.invoiceInfo }
    let modal = this.modal.open(SuccessInvoiceChanges, { centered: true, size: 'md' })
  }

  updateInvoiceCredit(form: NgForm, modal) {
    this.http.post(ApiUrls.covertToCredit, { data: { "to_invoice_number": form.value.invoiceNumber, "from_invoice_number": this.invoiceInfo?.name } }).subscribe((res: any) => {
      if (res?.message?.success) {
        modal.dismiss()
        this.toastr.success("A new invoice created in Manual Tax Invoice")
        this.location.back();
      } else {
        let errmsg = res?.message?.message.includes("Duplicate entry")
        if (errmsg) {
          this.toastr.error("Duplicate Invoice Number")
        } else {
          this.toastr.error()
        }
      }
    })
  }

  /**SAC ERR */
  addSacError(selectErrType) {
    let modal = this.modal.open(selectErrType, {
      size: 'md', centered: true
    })
    modal.result.then((res: any) => {
      // if (res) {
      //   this.reload(this.invoiceInfo?.invoice_file)
      // }

    })
  }

  addPayment(form, modal) {
    let formData = {
      payment_type: form.value.payment_type.trimEnd(),
      company: this.companyDetails?.name,
      status: "Active"
    }
    this.http.post(`${ApiUrls.paymentTypes}`, formData).subscribe((res: any) => {
      if (res.data) {
        this.reload(this.invoiceInfo?.invoice_file)
        this.toastr.success("Payment Added");
        modal.dismiss('Added');
      }

    })
  }
  selectRevenue() {
    const editSacCode = this.modal.open(SacHsnComponent, {
      size: 'lg',
      centered: true,
      windowClass: 'modal-sac',
      animation: false
    })
    editSacCode.componentInstance.sacHsnCodErr = this.getSacCode;
    editSacCode.result.then((res: any) => {
      this.reload(this.invoiceInfo?.invoice_file)
    })
  }
  help(howToSolve) {
    this.modal.open(howToSolve, {
      size: 'xl',
      centered: true,
    })
  }

  /**Auto Adjustment */
  adjustInvoices() {
    let data = { data: { invoice_number: this.invoiceInfo?.invoice_number } }
    this.http.post(ApiUrls.autoAdjustment, data).subscribe((res: any) => {
      if (res?.message?.success) {
        this.getInvoiceInfo();
        this.toastr.success(res.message.message)
      } else {
        this.toastr.error(res.message.message)
      }
    })
  }
  /******************************** */

  /**convert To Credit Note */
  convertToCreditForm(form: NgForm, modal) {
    if (form.valid) {
      let dataObj = {
        invoice_number: this.invoiceInfo?.invoice_number,
        invoice_date: form.value.invoice_date,
        taxinvoice: form.value.taxinvoice == true ? "Yes" : "No",
        taxinvoice_number: this.companyDetails?.create_taxinvoice_raisecredit == 'Yes' ? form.value.taxinvoice_number : `${this.invoiceInfo.invoice_number}-1`
      }
      this.http.post(ApiUrls.convertToCreditNote, { data: dataObj }).subscribe((res: any) => {
        // if (res?.message?.success) {
        //   this.getInvoiceInfo();
        //   this.toastr.success(res.message.message)
        // }
        if (res?.message?.success) {
          modal.dismiss()
          this.getInvoiceInfo();
          this.toastr.success(res.message.message)
        } else {
          let errmsg = res?.message?.message.includes("Duplicate entry")
          if (errmsg) {
            this.toastr.error("Duplicate Invoice Number")
          } else {
            this.toastr.error()
          }
        }
      })
    }
    // if (!window.confirm(`Are you sure to move Credit Note for Invoice ${this.invoiceInfo.name} ?`)) {
    //   return null;
    // } else {

    // }
  }
  convertToCredit(SuccessInvoiceCreditNote) {
    this.changeInvoiceForm = { ...this.invoiceInfo }
    let modal = this.modal.open(SuccessInvoiceCreditNote, { centered: true, size: 'md' })
  }
  /*************** */

  /**  Update GST Details from GSPortal */
  updateFromGSPortal() {
    this.http.post(ApiUrls.updateGSTRDetails, { data: { gstNumber: this.invoiceInfo?.gst_number, invoice_number: this.invoiceInfo?.invoice_number } }).subscribe((res: any) => {
      if (res) {
        this.getInvoiceInfo()
      }
    })
  }

  /*********** */


  getTotal(type) {
    let arr = this.invoiceInfo.items
    let newArr = arr.filter((item) => {
      if ((item.item_mode === 'Debit' || item.item_mode === 'Credit') && item.type === 'Included') {
        return item
      }
    })
    let result
    result = newArr.reduce((total, thing) => total + JSON.parse(thing.quantity), 0);

    return result;
  }


  exportInvoiceItem() {
    this.http.get(`${ApiUrls.exportInvoiceLineItems}`, {
      params: {
        filters: JSON.stringify([["parent", "=", `${this.invoiceInfo.invoice_number}`]])
      }
    }).subscribe((res: any) => {
      if (res?.message?.success) {
        const fileUrl = `${environment.apiDomain}${res?.message?.file_url}`
        window.open(fileUrl, '_blank');

      }
    })
  }

  viewBillModel(viewBill, item) {
    this.modal.open(viewBill, {
      size: 'lg',
      centered: true,
      windowClass: 'sideMenuPdf2',
    });

    this.http.get(`${ApiUrls.resource}/${Doctypes.posChecks}/${item.pos_check}`).subscribe((res: any) => {
      console.log('=======', res)
      if (res?.data) {
        this.pos_bill_data = res?.data
        console.log(this.pos_bill_data)
      }
    })

  }

  enableSezForAll() {
    console.log(this.selectAll)
    this.sortedListInvoice.forEach((res: any) => {
      res.manual_edit = 'Yes'
      if (this.selectAll) {
        res.lut_exempted = true
      } else {
        res.lut_exempted = false
      }
    })
    this.switchSEZ()
  }

  ngOnDestroy(): void {
    this.modal.dismissAll();
  }

  downloadRequestJson() {
    // console.log('===================', this.irnObject)
    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.irnObject?.irn_request_object));
    let dlAnchorElem = document.createElement('a')
    // var dlAnchorElem = document.getElementById('downloadAnchorElem');
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", "irn-request.json");
    dlAnchorElem.click();
  }

  downloadResponseJson() {
    // console.log('===================', this.irnObject)
    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.irnObject?.irn_response_object));
    let dlAnchorElem = document.createElement('a')
    // var dlAnchorElem = document.getElementById('downloadAnchorElem');
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", "irn-response.json");
    dlAnchorElem.click();
  }

  downlaod_e_tax_invoice() {
    let data = {
      invoice_number: this.invoiceInfo.invoice_number,
      e_tax_format: this.companyDetails.e_tax_format
      // based_on: 'user'
    }
    this.http.post(ApiUrls.add_signature_on_etax, data).subscribe((res: any) => {
      if (res?.message?.success) {
        // this.toastr.success(res?.message?.message)
        // const fileUrl = `${environment.apiDomain}${res?.message?.file}`
        // window.open(fileUrl, '_blank');
        console.log('=====', res?.file)
        let path = res?.message?.file;
        var link = document.createElement('a');
        link.href = `${this.apiDomain}${res.message.file}`;
        link.download = path;
        link.target = "_blank";
        link.click()
      }
    })
  }

  enableETaxInvoiceDownloadBtn() {
    if (this.companyDetails.e_signature == 'User') {
      this.http.get(`${ApiUrls.resource}/${Doctypes.userSignature}`, {
        params: {
          filters: JSON.stringify([['name', '=', this.loginData?.name]]),
          fields: JSON.stringify(['*'])
        }
      }).subscribe((res: any) => {
        if (res?.data?.length) {
          console.log('=======', res.data)
          this.eTaxInvoiceDownloadBtn = true
          this.signature_img = res.data[0]?.signature_image;
          this.signature_pfx = res.data[0]?.signature_pfx
          this.pfx_password = res.data[0]?.pfx_password;
        } else {
          this.eTaxInvoiceDownloadBtn = false
        }
      })
    } else if (this.companyDetails.e_signature == 'Organization') {
      this.signature_img = this.companyDetails?.signature_image;
      this.signature_pfx = this.companyDetails?.signature_pfx
      this.pfx_password = this.companyDetails?.pfx_password;
      if (this.signature_pfx) {
        this.eTaxInvoiceDownloadBtn = true
      } else {
        this.eTaxInvoiceDownloadBtn = false
      }
    } else {
      this.eTaxInvoiceDownloadBtn = false
    }

  }

}

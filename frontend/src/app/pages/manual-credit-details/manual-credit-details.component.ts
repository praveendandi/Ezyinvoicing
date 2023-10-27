import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, HostListener, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { NgForm, NgModel } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import * as Moment from 'moment';
import { environment } from 'src/environments/environment';
import { switchMap } from 'rxjs/operators';
import { UOMCode } from 'src/app/shared/uom-codes';
import { ActivitylogComponent } from '../activitylog/activitylog.component';
import { stateCode } from 'src/app/shared/state-codes';
import { CreateInvoiceManualComponent } from 'src/app/shared/models/create-invoice-manual/create-invoice-manual.component';
import { TempSacLineComponent } from 'src/app/shared/models/temp-sac-line/temp-sac-line.component';
import { degrees, PDFDocument } from 'pdf-lib';
import { SacHsnComponent } from 'src/app/shared/models/sac-hsn/sac-hsn.component';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
@Component({
  selector: 'app-manual-credit-details',
  templateUrl: './manual-credit-details.component.html',
  styleUrls: ['./manual-credit-details.component.scss']
})
export class ManualCreditDetailsComponent implements OnInit, OnDestroy {
  @ViewChild('invoicePdf') invoicePdf: ElementRef;
  @ViewChild('B2CtoB2CTemp') B2CtoB2CTemp: ElementRef;
  @ViewChild('emailTemp') emailTemp: ElementRef;
  @ViewChild('sezGenerateIRN') sezGenerateIRN: ElementRef;
  manualType;
  editData;
  creditItems = []
  creditInvoiceItem: any = {
    // unit_of_measurement_description: 'UNITS',
    // quantity: 1
    net: 'No'
  }
  invoiceInfo: any = {}
  invoiceNumber;
  sacCodeName;
  totalCount;
  sacCodeData;
  companyData;
  sacCodeDetails = []
  sort_order = 0;
  // sacCodeDate;
  sacCodePrice;
  sacDetails;
  apiDomain = environment.apiDomain;
  credit_Items: any = []
  gstDetails: any = {}
  formatDate;
  place_of_supply;
  isChecked = false;
  dupItems: any = []
  uomData: any = [];
  checkITemType;
  loginData;
  stateCode;
  stateCodeList;
  @ViewChild('addInvoiceModal') addInvoiceModal: ElementRef;
  today_date = Moment(new Date()).format('YYYY-MM-DD');
  apiMethod;
  date;
  checkSplit = false;
  addItemModelRef;
  previewFile;
  pdfListItems = [];
  invoicetypeName;
  invoicetype = true;
  pdfView = true;
  invoiceTitle;
  myDate = new Date();
  CreditInvoice = false
  TaxInvoice = false;
  pdfFile = '';
  taxPayerDetails: any = {};
  checkApiMethod = false;
  checkName = false;
  addNEwSacOption = false;
  notFoundSac;
  emailTempData: any = {};
  templatesList = [];
  disableEmailBtn = false;
  active = 1;
  sacEditForHICC = true;
  taxableArr = [];
  address1_state: any;
  address2_state: any;
  location_state: any;
  place_of_supply_state: any;
  printEnable = false;
  hindia_prop = 'HINDIA-01'//JP-2022
  loginUSerRole: any;
  changeInvoiceForm: any = {};
  pos_bill_data;
  signature_img: any = {}
  signature_pfx: any = {}
  pfx_password;
  eTaxInvoiceDownloadBtn: any;
  irnObject: any = {};
  paxEnableCompanyCode = 'RHV-01'
  checkIRNdate:any;
  @HostListener('window:beforeunload', ['$event'])
  unloadNotification($event: any) {
    $event.returnValue = true;
  }




  constructor(public toastr: ToastrService, private router: Router, private toaster: ToastrService, private activatedRoute: ActivatedRoute, private modal: NgbModal, private http: HttpClient, private activeRoute: ActivatedRoute) { }

  ngOnInit(): void {
    this.stateCodeList = stateCode;
    this.companyData = JSON.parse(localStorage.getItem('company'));
    console.log(this.companyData)
    this.companyData['pan_number'] = this.companyData?.gst_number.substr(2, 10);
    this.loginData = JSON.parse(localStorage.getItem('login'));
    if (this.loginData?.name == 'Administrator') {
      this.loginUSerRole = true;
    } else {
      this.loginUSerRole = this.loginData.rolesFilter.some((each: any) => (each == 'ezy-Finance'))
      if (this.companyData?.property_group == "HolidayIn Express") {
        console.log(" Accor")
        let sacEditRolesForHICC = this.loginData.rolesFilter.filter((each: any) => (each !== 'ezy-FrontOffice'))
        this.sacEditForHICC = sacEditRolesForHICC.length > 0 ? true : false;
      }

    }

    this.invoiceNumber = this.activeRoute.snapshot.params.id;
    this.activatedRoute.queryParams.subscribe((res: any) => {
      console.log("==type ===", res.type)
      this.manualType = res.type
    })
    // console.log(this.activeRoute.snapshot.params.id);
    this.getInvoiceData();
    // console.log(this.companyData);
    this.enableETaxInvoiceDownloadBtn()
  }

  switchSEZ() {

  }



  downlaod_e_tax_invoice() {
    let data = {
      invoice_number: this.invoiceInfo.invoice_number,
      // based_on: 'user',
      e_tax_format: this.companyData.e_tax_format
    }
    this.http.post(ApiUrls.add_signature_on_etax, data).subscribe((res: any) => {
      if (res?.message?.success) {
        // this.toastr.success(res?.message?.message)
        // const fileUrl = `${environment.apiDomain}${res?.message?.file}`
        // window.open(fileUrl, '_blank');
        console.log('=====', res?.e_tax_format)
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
    if (this.companyData.e_signature == 'User') {
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
    } else if (this.companyData.e_signature == 'Organization') {
      this.signature_img = this.companyData?.signature_image;
      this.signature_pfx = this.companyData?.signature_pfx
      this.pfx_password = this.companyData?.pfx_password;
      if (this.signature_pfx) {
        this.eTaxInvoiceDownloadBtn = true
      } else {
        this.eTaxInvoiceDownloadBtn = false
      }
    } else {
      this.eTaxInvoiceDownloadBtn = false
    }

  }


  convertToCredit(SuccessInvoiceCreditNote) {
    this.changeInvoiceForm = { ...this.invoiceInfo }
    let modal = this.modal.open(SuccessInvoiceCreditNote, { centered: true, size: 'md' })
  }
  convertToCreditForm(form: NgForm, modal) {
    if (form.valid) {
      let dataObj = {
        invoice_number: this.invoiceInfo?.invoice_number,
        invoice_date: form.value.invoice_date,
        taxinvoice: form.value.taxinvoice == true ? "Yes" : "No",
        taxinvoice_number: this.companyData?.create_taxinvoice_raisecredit == 'Yes' ? form.value.taxinvoice_number : `${this.invoiceInfo.invoice_number}-1`
      }
      this.http.post(ApiUrls.convertToCreditNote, { data: dataObj }).subscribe((res: any) => {
        // if (res?.message?.success) {
        //   this.getInvoiceInfo();
        //   this.toastr.success(res.message.message)
        // }
        if (res?.message?.success) {
          modal.dismiss()
          this.getInvoiceData();
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

  async addInvoice() {
    this.getCodesCount();
    this.creditInvoiceItem = {
      // unit_of_measurement_description: 'UNITS',
      // quantity: 1
    }
    this.sacDetails = ''
    this.uomData = UOMCode
    this.addItemModelRef = 'addItem'
    const modalRef = await this.modal.open(this.addInvoiceModal, {
      size: 'md',
      centered: true,
    });
    modalRef.result.finally(() => {
      this.addNEwSacOption = false;
      this.sacCodeName = null;
      // this.sacDetails = null;
      this.checkITemType = null;
    });
  }
  changeDescription(e, gst_number: NgModel): void {
    console.log(e);
    if (e && e.length == 15) {
      this.http.get(`${ApiUrls.getClient}?doctype=${Doctypes.TaxPayerDetail}&fieldname=name&filters=${e}`).subscribe((res: any) => {
        if (res.message) {
          const dataObj = { "data": { "code": this.companyData.company_code, "gstNumber": e } }
          this.http.post(`${ApiUrls.taxPayersDetails}`, dataObj).subscribe((res: any) => {
            try {
              if (res.message.success) {
                this.editData = { ...this.editData, ...res.message.data };
                this.editData.guest_name = res.message.data.legal_name;

                // this.editData.place_of_supply = stateCode.find((each)=> each.tin == this.editData.place_of_supply);
              } else {
                // GST number error
                gst_number.control.setErrors({ 'error': 'Invalid GST number' });
                gst_number.control.markAllAsTouched();
                // gst_number.control.markAllAsTouched();
                delete this.editData['legal_name'];
                delete this.editData['trade_name'];
                delete this.editData['state_code'];
                delete this.editData['address_1'];
                delete this.editData['address_2'];
                delete this.editData['pincode'];
                delete this.editData['location'];
              }

              if (res.message.success && res.message && !res.message?.update) {
                const body = {
                  address_1: this.editData.address_1,
                  address_2: this.editData.address_2,
                  block_status: "U",
                  company: this.companyData.name,
                  gst_number: this.editData.gst_number,
                  gst_status: this.editData.gst_status,
                  legal_name: this.editData.legal_name,
                  location: this.editData.location,
                  name: this.editData.gst_number,
                  phone_number: this.editData.phone_number,
                  pincode: this.editData.pincode,
                  state_code: this.editData.state_code,
                  status: this.editData.status,
                  tax_type: this.editData.tax_type,
                  trade_name: this.editData.trade_name,
                }
                this.http.post(`${ApiUrls.taxPayerDefault}`, this.editData).subscribe((res: any) => {
                  console.log(res);
                });
              }
            } catch (e) { console.log(e) }
          });
        }
      })
    }
  }


  getInvoiceData() {
    this.http.get(ApiUrls.creditInvoice + `/${this.invoiceNumber}`).subscribe((res: any) => {
      if (res) {
        this.invoiceInfo = res.data;

        let today_date: any = Moment(this.invoiceInfo?.invoice_date).format('YYYY-MM-DD')
          let date_expiry: any = this.companyData?.einvoice_missing_start_date ? Moment(this.companyData?.einvoice_missing_start_date).format('YYYY-MM-DD') : null
          
          if (this.companyData?.einvoice_missing_date_feature && (today_date >= date_expiry)) {
            let today_date: any = Moment(new Date()).format('YYYY-MM-DD') // new Date()
            let date_expiry: any = Moment(Moment(this.invoiceInfo.invoice_date).add(7, 'd').format('YYYY-MM-DD')) //new Date(this.invoiceInfo.invoice_date);
            date_expiry = Moment(date_expiry).format('YYYY-MM-DD')
            this.invoiceInfo['expiry_date'] = Moment(date_expiry).format('YYYY-MM-DD') //date_expiry
            this.invoiceInfo['expiry_days'] = Moment(date_expiry).diff(Moment(today_date), 'days') // Math.round(Math.abs((date_expiry - today_date) / oneDay))            
            this.checkIRNdate = date_expiry < today_date
          }

       

        this.invoiceInfo.gst_summaryTotal = (this.invoiceInfo.gst_summary as any[]).reduce((prev, nxt) => prev + parseFloat(nxt.amount), 0);
        this.getGSTDetailsbyInvoice();
        const generatedTime = new Date(this.invoiceInfo.irn_generated_time);
        generatedTime.setTime(generatedTime.getTime() + (25 * 60 * 60 * 1000));
        this.invoiceInfo.showCancelIrn = generatedTime >= new Date();
        this.place_of_supply = this.invoiceInfo.place_of_supply
        this.invoiceInfo.place_of_supply_name = stateCode.find((each) => each.tin == this.invoiceInfo.place_of_supply)?.state || 'NA';

        this.sacCodeDetails = res.data.items;
        this.sacCodeDetails = this.sacCodeDetails.sort((a, b) => parseFloat(a.sort_order) - parseFloat(b.sort_order))

        this.formatDate = Moment(this.invoiceInfo.invoice_date).format('DD-MMM-YY h:mm:ss');
        this.stateCode = stateCode.find((res: any) => res.tin === this.invoiceInfo.state_code)

        this.pdfListItems = this.invoiceInfo.items.sort((a, b) => parseFloat(a.sort_order) - parseFloat(b.sort_order));
        this.pdfFile = this.invoiceInfo?.invoice_file.trim()

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
          if (taxable == "Yes") {
            let key = Object.entries(r).join('-');
            acc[key] = (acc[key] || { ...r, item_value: 0, cgst_amount: 0, sgst_amount: 0, igst_amount: 0, cess: 0, cess_amount: 0, vat_amount: 0 });
            return (acc[key].item_value += item_value, acc[key].cgst_amount += cgst_amount, acc[key].sgst_amount += sgst_amount, acc[key].igst_amount += igst_amount, acc[key].cess += cess, acc[key].cess_amount += cess_amount, acc[key].vat_amount += vat_amount, acc);
          }
        }, {}));

        if ((this.companyData.name == "FMCOMR-01" || this.companyData.name == 'FPBSA-01' || this.companyData.name == 'HRC-01' || this.companyData.name == 'JWMC-01') && this.invoiceInfo?.irn_generated == "Success" && this.invoiceInfo?.invoice_type == "B2B") {
          this.getIrnObjectSuccess();
        }

        console.log(this.taxableArr);
      }
    })
  }


  getGSTDetailsbyInvoice(){
    this.http.get(ApiUrls.taxPayerDefault+'/'+this.invoiceInfo?.company_gst).subscribe((res:any)=>{
      if(res&& res?.data && res?.data?.name){
        this.invoiceInfo['company_fssai_number'] = this.companyData?.fssai_number;
        this.invoiceInfo['company_name'] = this.companyData?.company_name
        this.invoiceInfo['company_legal_name'] = res?.data?.legal_name;
        this.invoiceInfo['company_address_1'] = res?.data?.address_1
        this.invoiceInfo['company_address_2'] = res?.data?.address_2;
        this.invoiceInfo['company_location'] = res?.data?.location;
        this.invoiceInfo['company_pincode'] = res?.data?.pincode;
        this.invoiceInfo['company_state_code'] = res?.data?.state_code;
        this.invoiceInfo['company_logo'] = this.companyData?.company_logo
        this.invoiceInfo['company_place_of_supply'] = res?.data?.state_code;
        this.invoiceInfo['custom_e_tax_invoice_logo_image'] = this.companyData?.custom_e_tax_invoice_logo_image
      }
    })
  }


  register(form, index) {

    if (form.invalid) {
      form.form.markAllAsTouched();
      return;
    }
    const maxValueOfSort = Math.max(...this.invoiceInfo.items.map(o => o.sort_order), 0);
    let uomCode = UOMCode.find((res: any) => res.description === form.value?.unit_of_measurement_description)
    let string = this.companyData.invoice_item_date_format; // just an example
    string = string.replaceAll('%', '');
    string = string.replaceAll('d', 'DD');
    string = string.replaceAll('m', 'MM');
    string = string.replaceAll('b', 'MMM');
    string = string.replaceAll('Y', 'YYYY');
    string = string.replaceAll('y', 'YY');
    string = string.toUpperCase();
    this.date = Moment(this.invoiceInfo.invoice_date).format(string)
    if (this.addItemModelRef == 'addItem') {
      if (this.manualType == 'Credit') {
        let itemAmt = (this.companyData.company_code === this.hindia_prop || this.checkITemType === 'HSN') ? (form.value?.item_value * form.value?.quantity) : form.value?.item_value;
        form.value['item_value'] = -JSON.parse(itemAmt);
      } else {
        let itemAmt = (this.companyData.company_code === this.hindia_prop || this.checkITemType === 'HSN') ? (form?.value?.item_value * form?.value?.quantity) : form.value?.item_value;
        form.value['item_value'] = JSON.parse(itemAmt);
      }
    } else {
      if (this.manualType == 'Credit') {
        form.value['item_value'] = -JSON.parse(form.value.item_value)
      } else {
        form.value['item_value'] = JSON.parse(form.value.split_value ? form.value.split_value : form.value.item_value);
      }
    }

    // form.value['item_value'] = JSON.parse(form.value.split_value ? form.value.split_value : form.value.item_value);
    form.value['date'] = this.date;
    form.value['name'] = this.sacCodeName?.name ? this.sacCodeName?.name : this.sacCodeName;
    form.value['sac_code'] = 'No Sac';
    form.value['sort_order'] = Math.round(maxValueOfSort) + 1;;
    form.value['quantity'] = form.value.quantity || 1;
    form.value['unit_of_measurement_description'] = form.value.unit_of_measurement_description || 'OTHERS';
    form.value['unit_of_measurement'] = uomCode?.code || 'OTH';
    form.value['sez'] = this.invoiceInfo?.sez;
    form.value['invoice_number'] = this.invoiceInfo?.invoice_number;
    if (this.sacCodeDetails[index]) {
      this.sacCodeDetails[index]['split_value'] = form.value.split_value;
    }
    let temp = this.sacCodeDetails.map((each) => {
      if (each.item_name) {
        each.name = each.item_name;
        each.date = Moment(each.date).format(string)
        // each.date = this.companyData.invoice_item_date_format === '%d-%m-%y' ? Moment(each.date).format('DD-MM-YY') : Moment(each.date).format('DD/MM/YY');
      }
      return each
    });

    if (form.value?.split_value) {
      temp[index].item_value = this.creditInvoiceItem.value - (form.value.split_value);
    }
    // temp = temp.filter((each: any) => each?.is_service_charge_item == 'No')
    const data = {
      "data": {
        "items": [...temp, form.value],
        "place_of_supply": this.invoiceInfo?.place_of_supply,
        "company_code": this.companyData.company_code,
        "invoice_number": this.invoiceNumber,
        "invoice_item_date_format": this.companyData.invoice_item_date_format,
        "guest_data": {
          invoice_category: `${this.manualType} Invoice` //this.manualType == 'Credit' ? 'Credit Invoice' : 'Tax Invoice'
        }
      }
    }
    console.log(data);
    if (data) {
      this.http.post(ApiUrls.cal_items, data).subscribe((res: any) => {
        if (res.message) {
          this.sacCodeDetails = [...res.message.data || []];
          this.sacCodeDetails = this.sacCodeDetails.sort((a, b) => parseFloat(a.sort_order) - parseFloat(b.sort_order))
          this.toaster.success('Item created');
          this.modal.dismissAll(form.reset());
          this.saveItems()
        } else {
          this.toaster.error('Error');
          this.modal.dismissAll()
        }
      })
    }
  }

  // getCodesCount(): void {
  //   this.http.get(`${ApiUrls.sacHsn}`, {
  //     params: {
  //       fields: JSON.stringify(["count( `tabSAC HSN CODES`.`name`) AS total_count"])
  //     }
  //   }).subscribe((res: any) => {
  //     this.totalCount = res.data[0].total_count;
  //     this.getCodesData()
  //   })
  // }
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

  modelChangeFn(e, type, calAmt) {
    this.addNEwSacOption = false;

    if (!e) {
      return;
    }
    console.log("change func =====", e)
    if (type === 'name') {
      this.sacCodeName = e
      this.creditInvoiceItem.description = e.name;
      this.http.get(`${ApiUrls.sacHsn}/${e.name}`).subscribe((res: any) => {
        console.log(res)
        if (res) {
          this.checkITemType = res.data.type;
          console.log(this.checkITemType)
          this.creditInvoiceItem.quantity = this.checkITemType == 'HSN' ? 1 : this.companyData.company_code === this.hindia_prop ? 1 : null;
          this.creditInvoiceItem.unit_of_measurement_description = this.checkITemType == 'HSN' ? 'UNITS' : this.companyData.company_code === this.hindia_prop ? 'OTHERS' : null;
        }
      })
    }

    if (type === 'price') {
      if (calAmt && (this.hindia_prop || this.checkITemType === 'HSN')) {
        this.sacCodePrice = calAmt
      } else {
        this.sacCodePrice = e
      }
    }
    console.log(this.sacCodeName);

    if (this.sacCodeName && this.sacCodePrice) {
      if (this.addItemModelRef == 'splitItem') {
        if (!this.creditInvoiceItem.net) {
          return;
        }
      }
      let string = this.companyData.invoice_item_date_format; // just an example
      string = string.replaceAll('%', '');
      string = string.replaceAll('d', 'DD');
      string = string.replaceAll('m', 'MM');
      string = string.replaceAll('b', 'MMM');
      string = string.replaceAll('Y', 'YYYY');
      string = string.replaceAll('y', 'YY');

      string = string.toUpperCase();
      this.date = Moment(this.invoiceInfo.invoice_date).format(string)
      console.log("String ======", this.date)
      // if (this.companyData.invoice_item_date_format == '%d-%m-%y') {
      //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD-MM-YY')
      // }

      // if (this.companyData.invoice_item_date_format == '%d/%m/%y') {
      //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD/MM/YY')
      // }
      // if (this.companyData.invoice_item_date_format == '%d/%m/%Y') {
      //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD/MM/YYYY')
      // }

      // if (this.companyData.invoice_item_date_format == '%d.%m.%y') {
      //   this.date = Moment(this.invoiceInfo.invoice_date).format('DD.MM.YY')
      // }

      // const dateformat = date.getDate() + '-' + (date.getMonth() + 1) + '-' + (date.getFullYear().toString().substr(-2));
      const form = {
        "item_value": JSON.parse(this.sacCodePrice),
        "date": this.date,
        "name": this.sacCodeName.name,
        "sac_code": 'No Sac',
        "sort_order": this.sort_order + 1,
        "net": this.creditInvoiceItem.net
      }
      const data = {
        "data": {
          "items": [form],
          "company_code": this.companyData.company_code,
          "invoice_number": this.invoiceNumber,
          "place_of_supply": this.invoiceInfo?.place_of_supply,
          "invoice_item_date_format": this.companyData.invoice_item_date_format,
          "guest_data": {
            invoice_category: `${this.manualType} Invoice` // this.manualType == 'Credit' ? 'Credit Invoice' : 'Tax Invoice'
          }
        }
      }
      console.log(data)
      if (data) {
        this.http.post(ApiUrls.cal_items, data).subscribe((res: any) => {
          if (res.message) {
            const sacCodes = res.message.data;
            // this.sacDetails = sacCodes[sacCodes.length - 1]
            this.sacDetails = res.message.data[0]
          }
        })
      }
    }


  }

  /**Check SacNAme */
  checkSacName(e) {
    this.notFoundSac = e.target.value;
    this.creditInvoiceItem.description = e.target.value
    this.addNEwSacOption = false;
    let text = e.target.value.toUpperCase()
    const checkNAme = this.sacCodeData?.filter((word: any) => word.name.toUpperCase().includes(text))
    if (checkNAme.length == 0) {
      this.addNEwSacOption = true
    }
  }
  /* ******************************* */

  /** add Sac New */
  addNewSAc() {
    const modalData = this.modal.open(SacHsnComponent, {
      size: 'lg',
      centered: true,
      windowClass: 'modal-sac',
      animation: false
    });
    modalData.result.then((res: any) => {
      if (res) {
        this.getCodesData()
        this.getInvoiceData();
        this.addNEwSacOption = false;
      }

    })
  }
  /******************************* */
  // getCodesData(): void {
  //   let queryParams: any = { filters: [] }

  //   // console.log(this.place_of_supply)
  //   // if (this.companyData.state_code === this.place_of_supply) {
  //   //   queryParams = { filters: [] };
  //   // } else {
  //   //   queryParams = { filters: [] };
  //   // }


  //   if (this.sacCodeName) {
  //     queryParams.filters.push(['description', 'like', `%${this.sacCodeName}%`]);
  //   }

  //   queryParams.limit_start = 0
  //   queryParams.limit_page_length = this.totalCount;
  //   queryParams.order_by = "`tabSAC HSN CODES`.`creation` desc"
  //   queryParams.fields = JSON.stringify(["name"]);
  //   queryParams.filters = JSON.stringify(queryParams.filters);

  //   const countApi = this.http.get(`${ApiUrls.sacHsn}`, {
  //     params: {
  //       fields: JSON.stringify(["count( `tabSAC HSN CODES`.`name`) AS total_count"]),
  //       filters: queryParams.filters
  //     }
  //   });
  //   const resultApi = this.http.get(`${ApiUrls.sacHsn}`, { params: queryParams }).subscribe((res: any) => {
  //     this.sacCodeData = res.data;
  //   })

  // }



  saveItems() {
    // this.sacCodeDetails = this.sacCodeDetails.concat(this.creditItems);
    console.log("save ====", this.sacCodeDetails)
    const todayDate = Moment().format('YYYY-MM-DD h:mm:ss');
    const data = this.invoiceInfo
    this.invoiceInfo['items_data'] = this.sacCodeDetails
    this.invoiceInfo['company_code'] = this.companyData.company_code;
    this.invoiceInfo['total_invoice_amount'] = 0;
    this.invoiceInfo['invoice_number'] = this.invoiceInfo.invoice_number;
    this.invoiceInfo['amened'] = 'No';
    this.invoiceInfo['invoice_from'] = 'Web';
    this.invoiceInfo['place_of_supply'] = this.invoiceInfo?.place_of_supply;
    this.invoiceInfo['guest_data'] = {
      address1: this.invoiceInfo.address1,
      invoice_type: this.invoiceInfo.invoice_type,
      invoice_category: this.manualType == 'Credit' ? 'Credit Invoice' : this.manualType == 'Tax' ? 'Tax Invoice' : 'Debit Invoice',
      invoice_number: this.invoiceInfo.invoice_number,
      name: this.invoiceInfo.guest_name,
      gstNumber: this.invoiceInfo.gst_number,
      invoice_file: this.invoiceInfo.invoice_file,
      room_number: this.invoiceInfo?.room_number || 0,
      invoice_date: this.formatDate,
      confirmation_number: this.invoiceInfo?.confirmation_number || 0,
      print_by: this.companyData.company_code,
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
    this.http.post(ApiUrls.sac_items, {
      "data": data
    }).subscribe((res: any) => {
      if (res.message.success) {
        this.toaster.success('Successfully Created');
        this.getInvoiceData();
        this.creditItems = [];
        // this.router.navigate(['/home/manual-credit-notes'], { queryParams: { type: this.manualType } })
      } else {
        this.toaster.error('Error');
      }
    })
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
              await this.getInvoiceData();
              this.toaster.success("IRN generated successfully")
              modal.close();
            } else {
              this.toaster.error(res.message.message);

            }
          }, (err) => {
            console.log('err: ', err);

          });
        }
      })
    }
  }

  generateIrn(): void {
    if (this.companyData?.einvoice_missing_date_feature) {
    this.http.post(ApiUrls.validate_irn_gen_date, { "invoice_number": this.invoiceInfo?.invoice_number }).subscribe((resp: any) => {
      if (resp?.message?.success) {
        this.generateIRNFn()
      } else {
        this.toastr.error("IRN Generation Date is expired")
      }
    })
  }else{
    this.generateIRNFn()
  }
  }

  generateIRNFn(){
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
      if (this.invoiceInfo?.has_credit_items == "Yes" && this.manualType == 'Tax') {
        window.alert("Please adjust the allowances to generate IRN")
      } else {
        if (!window.confirm(`Are you sure to generate IRN number for Invoice ${this.invoiceInfo.name} ?`)) {
          return null;
        } else {
          const formData = new FormData();
          formData.append('method', 'generateIrn');
          formData.append('args', `{"invoice_number":"${this.invoiceInfo.name}"}`);
          formData.append('docs', JSON.stringify(this.invoiceInfo));
          const dataObj = {
            invoice_number: this.invoiceInfo.name,
            generation_type: 'Manual'
          }
          this.http.post(ApiUrls.generateIrn_new, { data: dataObj }).subscribe(async (res: any) => {
            console.log(res)
            if (res.message.success) {
              await this.getInvoiceData();
              // await this.getInvoiceInfo();
              // this.submitInvoice();
              this.toaster.success("IRN generated successfully")
              this.toaster.success(res.message.sync_message)
            } else {
              this.toaster.error(res.message.message)
            }

          });
        }
      }
    }
  }

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
      formData.append('docs', JSON.stringify(this.invoiceInfo));
      this.http.post(ApiUrls.generateIrn, formData).subscribe(async (res) => {
        await this.getInvoiceData();
        console.log("Cancel ====", res)
        this.submitInvoice();
      });
    }
  }


  private submitInvoice(): void {
    console.log("Submit")
    const formData = new FormData();
    formData.append('method', 'frappe.client.submit');
    formData.append('args', JSON.stringify({ doctype: Doctypes.invoices, name: this.invoiceInfo.name }));
    formData.append('doc', JSON.stringify(this.invoiceInfo));
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
      console.log("Frappe Cancel ====", res)
      const temp = new FormData();
      temp.append('doctype', Doctypes.invoices);
      temp.append('docname', this.invoiceInfo.name);
      return this.http.post(ApiUrls.amendDoc, temp);
    }))).subscribe((res) => {
      this.getInvoiceData();
    });

  }


  invoiceEdit(content): void {
    console.log(this.invoiceInfo);

    this.editData = JSON.parse(JSON.stringify(this.invoiceInfo));
    this.editData.place_of_supply = stateCode.find((each) => each.tin == this.editData.place_of_supply);

    // this.modal.open(content, {
    //   size: 'lg',
    //   centered: true
    // });
    const modalInfo = this.modal.open(CreateInvoiceManualComponent, { size: 'lg', centered: true })
    modalInfo.componentInstance.editInvoiceInfo = this.editData;
    modalInfo.result.then((res: any) => {
      console.log(res)
      if (res) {
        const temp = {};
        temp['confirmation_number'] = res.confirmation_number;
        temp['gst_number'] = res.gst_number;
        temp['guest_name'] = res.guest_name;
        temp['invoice_date'] = res.invoice_date;
        temp['invoice_type'] = res.gst_number ? "B2B" : "B2C";
        temp['room_number'] = res.room_number;
        temp['total_invoice_amount'] = res.total_invoice_amount;
        temp['sez'] = res.sez;
        temp['place_of_supply'] = res.place_of_supply.tin;
        temp['legal_name'] = res.legal_name;
        temp['trade_name'] = res.trade_name;
        temp['state_code'] = res.state_code;
        temp['address_1'] = res.address_1;
        temp['address_2'] = res.address_2;
        temp['pincode'] = res.pincode;
        temp['location'] = res.location;
        temp['tax_invoice_referrence_number'] = res?.tax_invoice_referrence_number;
        temp['tax_invoice_referrence_date'] = res?.tax_invoice_referrence_date;
        temp['note'] = res.note;
        this.http.put(ApiUrls.invoices + '/' + this.invoiceInfo.name, temp).subscribe((res) => {
          this.getInvoiceData();
        });
      }
    })
  }

  invoiceEditSuccess(content) {
    let modal = this.modal.open(content, { centered: true, size: 'md' })
  }

  onInvoiceSubmit(form: NgForm, modalRef): void {
    if (form.valid) {
      this.http.put(ApiUrls.invoices + '/' + this.invoiceInfo.name, form.value).subscribe((res) => {
        modalRef.close();
        this.getInvoiceData();
      });
    } else {
      form.form.markAllAsTouched();
    }
  }


  deleteItems(event, item) {
    if (item.checked) {
      item.checked = !item.checked;
    } else {
      item['checked'] = true;
      this.isChecked = true;
    }
    this.dupItems = this.sacCodeDetails.filter((each: any) => each.checked)
    if (this.dupItems.length) {
      this.isChecked = true;
    } else {
      this.isChecked = false;
    }
  }


  deleteItem() {
    this.dupItems = this.sacCodeDetails.filter((each: any) => !each.checked)
    console.log(this.dupItems);
    const todayDate = Moment().format('YYYY-MM-DD h:mm:ss');
    const data = this.invoiceInfo
    this.invoiceInfo['items'] = this.dupItems;
    this.invoiceInfo['items_data'] = this.dupItems;
    this.invoiceInfo['company_code'] = this.companyData.company_code;
    this.invoiceInfo['total_invoice_amount'] = this.invoiceInfo.total_invoice_amount;
    this.invoiceInfo['invoice_number'] = this.invoiceInfo.invoice_number;
    this.invoiceInfo['amened'] = 'No';
    this.invoiceInfo['invoice_from'] = 'Web';
    this.invoiceInfo['guest_data'] = {
      address1: this.invoiceInfo.address1,
      invoice_type: this.invoiceInfo.invoice_type,
      invoice_category: `${this.manualType} Invoice`,//  this.manualType == 'Credit' ? 'Credit Invoice' : 'Debit Invoice',
      invoice_number: this.invoiceInfo.invoice_number,
      name: this.invoiceInfo.guest_name,
      gstNumber: this.invoiceInfo.gst_number,
      invoice_file: this.invoiceInfo.invoice_file,
      room_number: this.invoiceInfo.room_number,
      invoice_date: this.formatDate,
      confirmation_number: this.invoiceInfo.confirmation_number,
      print_by: this.companyData.company_code,
      // membership: 0,
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
        this.toaster.success('Successfully Deleted');
        this.getInvoiceData();
        this.isChecked = false;
      } else {
        this.toaster.error('Error');
      }
    })



  }


  print() {
    let head: any = document.getElementsByClassName('credit-details')[0]
    let style: any = document.createElement('style');
    if (this.companyData.e_tax_format == 'Landscape') {
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
    window.print();
  }

  manualSynctoGST() {
    let data = {
      invoice_number: this.invoiceInfo.invoice_number,
      doctype: Doctypes.invoices
    }
    this.http.post(ApiUrls.sync_data_to_erp_single, data).subscribe((res: any) => {
      if (res.message.success) {
        this.toastr.success(res.message.message);
        this.getInvoiceData();
      } else {
        this.toastr.error(res.message.message)
      }
    })
  }


  goBack() {
    if (this.creditItems.length > 0 && this.invoiceInfo.irn_generated !== 'Success' && this.invoiceInfo.irn_generated !== 'Cancelled') {
      if (window.confirm('Newly added items are not saved. Are sure to navigate back?')) {
        this.router.navigate(['home', 'manual-credit-notes'], { replaceUrl: true, queryParamsHandling: 'preserve' });
      }
    } else {
      this.router.navigate(['home', 'manual-credit-notes'], { replaceUrl: true, queryParamsHandling: 'preserve' });
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

  reAttachInvoice(): void {

    this.http.post(ApiUrls.reAttach, { invoice_number: this.invoiceInfo.invoice_number }).subscribe((res: any) => {
      if (res.message.success) {
        this.toaster.success(res.message.message);
        this.getInvoiceData();
      } else {
        this.toaster.error(res.message.message)
      }
    })
  }


  /**Delete Invoice */
  deleteInvoices() {
    if (!window.confirm(`Are you sure to delete Invoice? `)) {
      return null;
    } else {
      this.http.delete(`${ApiUrls.invoices}/${this.invoiceInfo?.name}`).subscribe((res: any) => {
        console.log(res);
        if (res?.message == 'ok') {
          this.toaster.success("This invoice is deleted")
          this.goBack();
        }
      })
    }
  }


  /**Line item edit */

  typeOf(value) {
    return value % 1 != 0
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
      console.log("res ====", res, index);
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
        items_data: this.checkSplit ? this.dupItems : this.invoiceInfo?.items,
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
        sez: this.invoiceInfo.sez
      }
    }
    console.log("manual Obj ======", manualEditObj)
    this.http.post(ApiUrls.tempLineItemEdit, manualEditObj).subscribe((res: any) => {
      console.log(res);
      if (res?.message?.success) {

        this.getInvoiceData();
      }
    })
  }



  /**Split Line Item */

  async splitLineItemModel(item, index) {
    this.addItemModelRef = "splitItem"
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

  /**Pdf */
  openInvoice() {
    this.fileType('Original Invoice');
    this.modal.open(this.invoicePdf, {
      size: 'lg',
      centered: true,
      windowClass: 'sideMenuPdf',
    });
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

  async fileType(title: string, returnFile = false) {
    console.log("title ====", title)
    this.pdfView = true;
    let qrPng;
    this.invoiceTitle = title;
    if (title == "Original Invoice") {
      this.invoiceTitle = title;
      qrPng = '';
      this.previewFile = this.apiDomain + this.invoiceInfo?.invoice_file;
      return;
    }
    if (title == "Tax Invoice" && this.invoiceInfo.invoice_type == 'B2B') {
      console.log('Tax Invoice B2B')
      qrPng = this.invoiceInfo.qr_code_image;
    }
    if (title == "Tax Invoice with Credits") {
      qrPng = this.invoiceInfo.credit_qr_code_image;
    }
    if (title == "Tax Invoice" && this.invoiceInfo.invoice_type == 'B2C') {
      console.log("'Tax Invoice' B2C")
      qrPng = this.invoiceInfo.b2c_qrimage;
    }
    // this.previewFile = type
    let xyz = this.apiDomain + this.invoiceInfo?.invoice_file;
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
        x: parseInt(this.companyData.qr_rect_x0),
        y: firstPage.getHeight() - parseInt(this.companyData.qr_rect_y0) - parseInt(this.companyData.qr_rect_y1),
        width: parseInt(this.companyData.qr_rect_x1),
        height: parseInt(this.companyData.qr_rect_y1)
      });
      // if (this.invoiceInfo?.invoice_type == 'B2B') {
      //   const page = this.companyData.irn_details_page === 'Last' ? pages[pages.length - 1] : pages[0];

      //   page.drawText(`IRN : ${this.invoiceInfo?.invoice_category == 'Credit Invoice'? this.invoiceInfo?.credit_irn_number : this.invoiceInfo?.irn_number}    ACK : ${ this.invoiceInfo?.invoice_category == 'Credit Invoice'? this.invoiceInfo?.credit_ack_no:  this.invoiceInfo?.ack_no}    Date : ${this.invoiceInfo?.invoice_category == 'Credit Invoice'? this.invoiceInfo?.credit_ack_date : this.invoiceInfo?.ack_date }`, {
      //     x: this.companyData?.irn_text_point1,
      //     y: page.getHeight() - parseInt(this.companyData.irn_text_point2),
      //     // y: this.companyDetails?.irn_text_point2,
      //     size: 8,
      //   });
      // }

      if (this.invoiceInfo?.invoice_type == 'B2B') {
        if (this.companyData.irn_text_alignment === "Horizontal") {
          const page = this.companyData.irn_details_page === 'Last' ? pages[pages.length - 1] : pages[0];

          page.drawText(`IRN : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_irn_number : this.invoiceInfo?.irn_number}    ACK : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_ack_no : this.invoiceInfo?.ack_no}    Date : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_ack_date : this.invoiceInfo?.ack_date}`, {
            x: this.companyData?.irn_text_point1,
            y: page.getHeight() - parseInt(this.companyData.irn_text_point2),
            size: 8
          });
        } else {
          const page = this.companyData.irn_details_page === 'Last' ? pages[pages.length - 1] : pages[0];

          page.drawText(`IRN : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_irn_number : this.invoiceInfo?.irn_number}    ACK : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_ack_no : this.invoiceInfo?.ack_no}    Date : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_ack_date : this.invoiceInfo?.ack_date}    GSTIN : ${this.invoiceInfo?.gst_number}`, {
            x: 10, y: 25, rotate: degrees(90), size: 8
          });

        }

      }
      const pdfDataUri = await pdfDoc.saveAsBase64({ dataUri: true, addDefaultPage: true });
      this.previewFile = pdfDataUri;
      // console.log("Preview File",this.previewFile)
    } else {
      console.log('QR img not found');

    }
  }

  /**Generate OR */
  generateQr(): void {
    if (!window.confirm(`Are you sure to generate QR number for Invoice ${this.invoiceInfo.name} ?`)) {
      return null;
    } else {
      const formData = new FormData();
      formData.append('invoice_number', this.invoiceInfo.invoice_number)
      this.http.post(ApiUrls.generateQR, formData).subscribe(async (res: any) => {
        if (!res.message.success) {
          this.toaster.error(res.message.message)
        }
        if (res.message.success) {
          await this.getInvoiceData();
          this.toaster.success("QR generated successfully")
        }

      });
    }
  }

  /**Convert B2C */
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
      converted_from_b2b_time: Moment(new Date()).format('YYYY-MM-DD h:mm:ss')
    }
    this.http.put(ApiUrls.invoices + '/' + this.invoiceInfo.name, dataObj).subscribe((res: any) => {
      // console.log(res)
      if (res.data) {
        this.getInvoiceData();
      }

    });
  }
  /**Convert B2B & B2C */
  openConvertModal(): void {
    // this.http.post(ApiUrls.validate_irn_gen_date, { "invoice_number": this.invoiceInfo?.invoice_number }).subscribe((resp: any) => {
    //   if (resp?.message?.success) {

        this.taxPayerDetails = {};
        this.checkApiMethod = false;
        let modal = this.modal.open(this.B2CtoB2CTemp, { centered: true, size: 'md' })


        this.taxPayerDetails.company = this.companyData?.name

    //   } else {
    //     this.toastr.error("IRN Generation Date is expired")
    //   }
    // })
  }
  changeGST(e): void {
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
              this.toaster.error(res.message.message);
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
                converted_from_b2c: 'Yes',
                converted_from_b2c_by: login?.full_name,
                converted_from_b2c_time: Moment(new Date()).format('YYYY-MM-DD h:mm:ss')
              }
              this.http.put(ApiUrls.invoices + '/' + this.invoiceInfo.name, dataObj).subscribe((res) => {
                this.modal.dismissAll();
                this.getInvoiceData();
              });
            }
          } catch (e) { console.log(e) }
        })
      }

    } else {
      form.form.markAllAsTouched();
    }
  }
  /**Email Templates */
  async openEmailTemp() {
    this.emailTempData.attachments = [];
    this.disableEmailBtn = false;
    let filesToBeUpload = [];
    // if (this.invoiceInfo?.invoice_from == "Pms") {
    //   if (this.invoiceInfo?.has_credit_items == "Yes") {
    //     filesToBeUpload.push('Tax Invoice', 'E-credits');
    //   } else {
    //     filesToBeUpload.push('Tax Invoice');
    //   }
    // } else {
    //   if (this.invoiceInfo?.invoice_type == 'B2B') {
    //     if (this.invoiceInfo?.has_credit_items == "Yes") {
    //       filesToBeUpload.push('E-Tax', 'E-Credit');
    //     } else {
    //       filesToBeUpload.push('E-Tax');
    //     }
    //   } else {
    //     filesToBeUpload.push('PMS Invoice');
    //   }
    // }
    if (this.invoiceInfo?.invoice_type == 'B2B') {
      if (this.invoiceInfo?.has_credit_items == "Yes") {
        filesToBeUpload.push('E-Credit');
      } else {
        filesToBeUpload.push('E-Tax');
      }
    } else {
      filesToBeUpload.push('PMS Invoice');
    }
    let filesForEmailTemp = [];
    filesToBeUpload.forEach(async (each: any, index) => {
      const formData = new FormData();
      if (this.invoiceInfo?.invoice_from !== 'File') {
        const file = await this.generatePdf();
        formData.append('file', file, `${each}.pdf`);
      }
      // else {
      //   if(this.invoiceInfo?.invoice_type == 'B2B' && this.invoiceInfo?.has_credit_items == "Yes"){
      //     const file = await this.generatePdf();
      //     formData.append('file', file, 'credit.pdf');
      //   }
      //   if(this.invoiceInfo?.invoice_type == 'B2B' && this.invoiceInfo?.has_credit_items == "No"){
      //     const file = await this.generatePdf();
      //     formData.append('file', file, 'e-tax.pdf');
      //   }
      //   if(this.invoiceInfo?.invoice_type == 'B2C'){
      //     const file = await this.generatePdf();
      //     formData.append('file', file, 'pms.pdf');
      //   }
      // }
      formData.append('is_private', '1');
      formData.append('folder', 'Home');
      formData.append('doctype', Doctypes.invoices);
      formData.append('fieldname', 'invoice');
      formData.append('docname', this.invoiceInfo.name);
      this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
        if (res) {
          filesForEmailTemp.push(res.message.name)
          console.log("==========", index + 1, "--------", filesToBeUpload.length)
          if (index + 1 == filesToBeUpload.length) {
            this.http.post(ApiUrls.emailTemplates, {
              invoice_number: this.invoiceInfo.invoice_number,
              templateFiles: filesForEmailTemp
            }).subscribe((data: any) => {
              if (data.message) {
                this.emailTempData = data.message;
                this.emailTempData.deleteFile = filesForEmailTemp;
                // console.log("this.emailTempData.attachments ====",this.emailTempData)
              } else {
                this.toaster.error()
              }

            });
          }
        } else {
          this.toaster.error()
        }
      })
    })

    let modal = this.modal.open(this.emailTemp, { centered: true, size: 'lg' });
    modal.result.then((res) => '', () => '').catch((err) => err).finally(() => {

    })

  }

  generatePdf(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        // if (this.invoiceInfo?.has_credit_items == "Yes" && this.invoiceInfo?.invoice_type == "B2B") {
        var div = document.getElementById('pmsCreditPDF');
        // } else if (this.invoiceInfo?.has_credit_items == "No" && this.invoiceInfo?.invoice_type == "B2B") {
        //   var div = document.getElementById('PmsTaxPdf');
        // } else {
        //   var div = document.getElementById('pmsPDF');
        // }
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

  async emailForm(form: NgForm, modalRef) {
    if (form.valid) {
      const formData = new FormData();
      formData.append('recipients', this.emailTempData.val.recipients);
      formData.append('subject', this.emailTempData.val.subject);
      formData.append('content', this.emailTempData.val.response);
      formData.append('doctype', Doctypes.invoices);
      formData.append('name', this.invoiceInfo.invoice_number);
      formData.append('attachments', JSON.stringify(this.emailTempData.attachments))
      formData.append('send_email', "1");
      formData.append('send_me_a_copy', "0");
      formData.append('email_template', this.emailTempData.val.name);
      formData.append('read_receipt', "0");
      formData.append('now', "true");
      this.disableEmailBtn = true;
      this.http.post(ApiUrls.sendEmail, formData).subscribe((res: any) => {
        if (res.message) {
          setTimeout(() => {
            this.http.get(`${ApiUrls.resource}/${Doctypes.emailLogs}`, {
              params: {
                fields: JSON.stringify(['reference_name', 'name', 'status']),
                filters: JSON.stringify([['reference_name', '=', this.invoiceInfo.name], ['status', '!=', 'Sent']])
              }
            }).subscribe((res: any) => {
              this.toaster.success('Email Successfully Sent');
              this.modal.dismissAll();
            })
          }, 3000);
        } else {
          this.toaster.error()
        }
      })
    } else {
      form.form.markAllAsTouched();
    }
  }
  /**Auto Adjustment */
  adjustInvoices() {
    let data = { data: { invoice_number: this.invoiceInfo?.invoice_number } }
    this.http.post(ApiUrls.autoAdjustment, data).subscribe((res: any) => {
      console.log(res)
      if (res?.message?.success) {
        this.getInvoiceData();
        this.toaster.success(res.message.message)
      } else {
        this.toaster.error(res.message.message)
      }
    })
  }
  /******************************** */

  /**  Update GST Details from GSPortal */
  updateFromGSPortal() {
    this.http.post(ApiUrls.updateGSTRDetails, { data: { gstNumber: this.invoiceInfo?.gst_number, invoice_number: this.invoiceInfo?.invoice_number } }).subscribe((res: any) => {
      if (res) {
        this.getInvoiceData()
      }
    })
  }

  /*********** */

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
    this.place_of_supply_state = this.invoiceInfo?.place_of_supply_name
  }

  modelChangeFn1(e) {
    this.place_of_supply = e.tin
  }
  updateInvoicePOS(form: NgForm, modalRef) {
    if (form.valid) {
      this.http.put(ApiUrls.invoices + '/' + this.invoiceInfo.name, { place_of_supply: form.value?.place_of_supply?.tin }).subscribe((res) => {
        modalRef.close();
        this.tempLineItemEditApi();
        this.toaster.success("Tax Payer Details updated")
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
        this.getInvoiceData();
        this.toaster.success("Tax Payer Details updated")
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
        this.getInvoiceData();
        this.toaster.success("Tax Payer Details updated")
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
        this.getInvoiceData();
        this.toaster.success("Tax Payer Details updated")
        // this.tempLineItemEditApi();
        // this.reload(this.invoiceInfo?.invoice_file)
      });
    } else {
      form.form.markAllAsTouched();
    }

  }


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
  printPdf() {
    this.printEnable = true;
    window.print();

  }
  stringToNumber(value) {
    console.log(typeof value)
    return parseFloat(value)
  }

  viewBillModel(viewBill, item) {
    this.modal.open(viewBill, {
      centered: true,
    });

    this.http.get(`${ApiUrls.resource}/${Doctypes.posChecks}/${item.pos_check}`).subscribe((res: any) => {
      console.log('=======', res)
      if (res?.data) {
        this.pos_bill_data = res?.data
        console.log(this.pos_bill_data)
      }
    })

  }
  ngOnDestroy(): void {
    this.modal.dismissAll();
  }


  potraitView() {

  }


  downloadIrnObj(data_obj) {
    // console.log('===================', data_obj)
    if (data_obj) {
      var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data_obj));
      let dlAnchorElem = document.createElement('a')
      // var dlAnchorElem = document.getElementById('downloadAnchorElem');
      dlAnchorElem.setAttribute("href", dataStr);
      dlAnchorElem.setAttribute("download", "irn-request.json");
      dlAnchorElem.click();
    }
  }


  getIrnObjectPending() {
    this.http.post(ApiUrls.pendingIrnObj, { invoice_number: this.invoiceInfo?.invoice_number }).subscribe((res: any) => {
      if (res?.message?.success) {
        this.irnObject = res?.message?.data
      }
    })
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


  irnModel(viewModel) {
    this.irnObject = {}
    this.fileType('Original Invoice');
    this.modal.open(viewModel, {
      size: 'md',
      centered: true,
      windowClass: 'sideMenuPdf2',
    });
    if (this.invoiceInfo?.irn_generated == "Pending" && this.invoiceInfo?.invoice_type == "B2B") {
      this.getIrnObjectPending();
    }
    if (this.invoiceInfo?.irn_generated == "Success" && this.invoiceInfo?.invoice_type == "B2B") {
      this.getIrnObjectSuccess();
    }
  }

}


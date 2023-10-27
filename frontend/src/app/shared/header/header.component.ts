import { NgForm } from '@angular/forms';
import { Location } from '@angular/common';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, EventEmitter, NgZone, OnDestroy, OnInit, Output, ViewChild } from '@angular/core';
import { ActivatedRoute, NavigationEnd, NavigationStart, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ApiUrls, Doctypes } from '../api-urls';
import { SocketService } from '../services/socket.service';
import { UserService } from '../services/user.service';
import { ToastrService } from 'ngx-toastr';
import { debounceTime, filter, map, switchMap, takeUntil } from 'rxjs/operators'
import { combineLatest, merge } from 'rxjs';
import * as moment from 'moment';
import { NotificationsComponent } from '../models/notifications/notifications.component';
import { CustomToastrComponent, IToastButton } from '../custom/custom-toastr/custom-toastr.component';
import { environment } from 'src/environments/environment';
import { AnimationItem } from 'lottie-web';
import { AnimationOptions } from 'ngx-lottie';
import { PDFDocument } from 'pdf-lib';
import { CookieService } from 'ngx-cookie-service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})


export class HeaderComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('selectPrinter') selectPrinter: ElementRef;
  @ViewChild('updating') updating: ElementRef;

  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  data=10
  company;
  companyDetails;
  userData;
  loginUSerRole;
  emailId;
  networkStatus = false;
  printers = [];
  // checkPrinter;
  new_password;
  selected;
  selectedValue;
  docTypes = [
    { name: 'SAC HSN CODES' },
    { name: 'Invoices' },
    { name: 'Credit Note Items' },
    { name: 'TaxPayerDetail' },
    { name: 'Payment Types' },
    { name: 'User' },
    { name: 'Role' },
    { name: 'Report' },
    { name: 'Deleted Documents' },
    { name: 'Upload Invoice' },
    { name: 'Email Queue' },
    { name: 'POS Bills' },
    { name: 'POS Bill Settings' },
    { name: 'Outlets' },
    { name: 'Print IP' }
  ]
  userRoles: any = []
  permissions: any = [];
  searchText;
  history; history2;
  update = false;
  updateUI = false;
  tagUpdate;
  branchUpdate;
  screenAdjust = false;
  activeLinkName = '';
  loginUser;
  apiDomain = environment.apiDomain;
  notificationsList = [];
  newCount = false;
  progressInfos: any = {};
  public isCollapsed = false;
  public isCollapsedOne = false;
  public isCollapsedTwo = false;
  toastRef;
  toastButtons: IToastButton[] = [
    {
      id: "1",
      title: "Print"
    },
    // {
    //   id: "2",
    //   title: "View"
    // }
  ];
  options: AnimationOptions = {
    path: '/assets/jsons/loading-bar.json',
  };
  emailLogUsers: any;
  loginFrontOfcUser = false;
  bulkUploadExcel = false;
  wrong_password :any ;
checkPOSvthFrontOfc :any = false;
change_user_details:any = {}
posUser = false;
  constructor(
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private http: HttpClient,
    private modal: NgbModal,
    private socketService: SocketService,
    private toaster: ToastrService,
    private cookie : CookieService
  ) { }

  ngOnInit(): void {
    if(this.router.url === "/home/dashboard"){
     this.screenAdjust = true;
    } else {
      this.screenAdjust = false;
    }
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    if(!this.companyDetails?.name){
      this.getCompanyData();
    }


    this.loginUser = JSON.parse(localStorage.getItem('login'))
    this.posUser = this.loginUser.rolesFilter.some((each:any)=> (each == 'ezy-Pos'))
    this.loginUSerRole = this.loginUser.rolesFilter.some((each:any)=> (each == 'ezy-IT'))
    this.loginFrontOfcUser = this.loginUser.rolesFilter.some((each:any)=> (each == 'ezy-FrontOffice'))
    // this.checkPOSvthFrontOfc = this.loginUser.rolesFilter.filter((each:any)=> (each == 'ezy-FrontOffice' && each == 'ezy-Pos'))
    let xyz = ['ezy-FrontOffice','ezy-Pos']
    this.checkPOSvthFrontOfc = xyz.reduce((a, b) => a && this.loginUser.rolesFilter.includes(b), true);
    console.log(this.checkPOSvthFrontOfc)
    this.emailLogUsers = this.loginUser.rolesFilter.some(function (each) {
      if (each == 'ezy-IT' || each =='ezy-FrontOffice' || each =='ezy-Finance') {
        return true;
      }
    })
    if(this.loginUSerRole || this.emailLogUsers || this.loginFrontOfcUser){
      this.posUser = false;
    }   
    const temp = this.activatedRoute.firstChild.snapshot;
    this.updateActiveLink(temp.data.name, temp.queryParams?.type);
    this.socketService.connectMe();
    this.router.events.pipe(filter(event => event instanceof NavigationEnd),
      map(() => {
        if(this.router.url === "/home/dashboard"){
          this.screenAdjust = true;
         } else {
           this.screenAdjust = false;
         }
        return this.activatedRoute;
      }),
      map(route => route.firstChild),
      switchMap(route => combineLatest(route.data, route.queryParams)),
      map(data => ({ name: data[0].name, params: data[1] }))
    ).subscribe((event) => {
      this.updateActiveLink(event.name, event.params?.type);
    });
    this.router.events.subscribe((event) => {
      if (event instanceof NavigationStart) {
        let historyUrl = event.url;
        let checkUrl = historyUrl.includes('/home/invoices?');
        if (checkUrl) {
          let searchParams: any = new URLSearchParams(historyUrl.split('?')[1]);
          searchParams = Array.from(searchParams as any).reduce((prev, nxt) => {
            prev[nxt[0]] = nxt[1];
            return prev;
          }, {})
          this.history = searchParams;
        }

        let checkUrl2 = historyUrl.includes('/home/amend-invoices?');
        if (checkUrl2) {
          let searchParams: any = new URLSearchParams(historyUrl.split('?')[1]);
          searchParams = Array.from(searchParams as any).reduce((prev, nxt) => {
            prev[nxt[0]] = nxt[1];
            return prev;
          }, {})
          this.history2 = searchParams;
        }

      }
    })

    this.socketService.newInvoice.pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
      if (!res) { return }
      if (res.message.type === 'bench update') {
        let modal = this.modal.open(this.updating, { centered: true, size: 'md', backdrop: 'static' })
        setTimeout((res: any) => {
          this.progressInfos = { uploadProgress: 25, color: 'info' };
        }, 1500)
      }
      // if (res.message.type === 'bench completed') {
      //   setTimeout((res: any) => {
      //     this.http.get(`${ApiUrls.migrateBench}`).subscribe((res: any) => {
      //       if (res.message.success) {
      //         this.progressInfos.uploadProgress = 70;
      //         setTimeout((rs: any) => {
      //           this.http.post(`${ApiUrls.Uiupdate}`, { "company": this.companyDetails.name }).subscribe((response: any) => {
      //             this.progressInfos.uploadProgress = 100;
      //             if(this.companyDetails?.proxy == 1){
      //               this.http.post(ApiUrls.checkProxy, { data: { company: this.companyDetails?.name, type: 'unset' } }).subscribe((proxy: any) => {
      //                 setTimeout((res: any) => {
      //                   if (proxy) {
      //                     this.modal.dismissAll()
      //                     localStorage.clear();
      //                     this.router.navigate([''])
      //                   }
      //                 }, 1500)
      //               })
      //             }else{
      //               setTimeout((res: any) => {
      //                 if (response) {
      //                   this.modal.dismissAll()
      //                   localStorage.clear();
      //                   this.router.navigate([''])
      //                 }
      //               }, 1500)
      //             }



      //           })
      //         }, 15000)


      //       }
      //     })
      //   }, 20000)



      // }

      if (res?.message?.message === 'Invoices Created') {
        this.showToast(res?.message,'invoice')
        this.newCount = true;
      }
      if (res?.message?.message === 'Invoice deleted') {
        this.toaster.info(`${res.message?.invoice_number} is deleted`)
        this.newCount = true;
      }
      if (res?.message?.type === 'Bulk_upload_invoice_count' || res?.message?.type === 'Bulk_file_invoice_created' || res?.message?.type === 'Bulk_upload_data') {
        // console.log(res?.message?.type)
        this.bulkUploadExcel = true
        // console.log(this.bulkUploadExcel)
      }

    })


    merge(this.socketService.newPosChecks.pipe(takeUntil(this.destroyEvents)))
    .pipe(debounceTime(300)).subscribe((data) =>{
      if(!data){return;}
      this.toaster.success(`New Check ${data.data?.check_no || ''} Added`)
    });



  }
  private updateActiveLink(name, param) {
    if (name == 'Manual Credit Notes') {
      if (param == 'Credit') {
        this.activeLinkName = 'Credit Notes';
      } else if (param == 'Debit') {
        this.activeLinkName = 'Debit Notes';
      } else if (param == 'Tax') {
        this.activeLinkName = 'Manual Tax Invoices';
      } else {
        this.activeLinkName = name;
      }
    } else {
      this.activeLinkName = name;
    }
  }
  animationCreated(animationItem: AnimationItem): void {
    console.log(animationItem);
  }
  onLoopComplete(): void {
    NgZone.assertNotInAngularZone();
    console.log(NgZone.isInAngularZone()); // false
  }
  updateGspTokens(companyInfo) {
    this.http.get(ApiUrls.gspApis + '/' + companyInfo.provider).subscribe((res: any) => {
      if (res.data) {
        const tokenDate = res.data.mode == 'Testing' ? res.data?.test_token_generated_on : res.data.prod_token_generated_on;
        const secondsToAdd = parseInt(res.data.mode == 'Testing' ? res.data.gsp_test_token_expired_on : res.data.gsp_prod_token_expired_on);
        const expired = !moment(tokenDate).add(secondsToAdd, 'seconds').isSameOrAfter(new Date());
        if (expired || tokenDate == undefined) {
          this.http.post(ApiUrls.gspToken, {
            data: {
              code: companyInfo.name,
              mode: res.data.mode
            }
          }).subscribe((res) => {
            console.log(res);
          })
        }
      }

    })
  }
  ngAfterViewInit() {
    // if (!this.checkPrinter) {
      // this.getPrinterData();
    // }
  }

  getCompanyData(){
    this.http.get(ApiUrls.company).subscribe((res: any) => {
      this.company = res.data[0];
      if (this.company) {
        this.http.get(ApiUrls.company + '/' + this.company?.name).subscribe((res: any) => {
          this.companyDetails = res.data;
          localStorage.setItem("company", JSON.stringify(res.data))
          this.updateGspTokens(res.data);
          this.getNetworkStatus();
        });
      }
    })
  }
  getPrinterData() {
    this.printers = [];
    this.http.get(ApiUrls.getPrinters).subscribe((res: any) => {
      if (res.message.success) {
        this.printers = res.message?.data;
        if (res.message?.data.length) {
          let printerModal = this.modal.open(this.selectPrinter, { centered: true, size: 'md' });
        }
      }
    })

  }

  selectedMenu(item) {
    if(item === 'CLBS'){
      window.open('/clbs', '_blank', 'noopener=1');
    }else if(item === 'GST'){
      window.open('/gstr','_blank', 'noopener=1');
    }else if(item === 'SYNC'){
      window.open('/sync','_blank', 'noopener=1');
    }
    else{
    if (item === 'Invoices') {
      if (this.history) {
        this.router.navigate(['/home/invoices'], { queryParams: this.history })
      } else {
        this.router.navigate(['/home/invoices']);
      }
    }
    if (item === 'Amended Invoices') {
      if (this.history2) {
        this.router.navigate(['/home/amend-invoices'], { queryParams: this.history2 })
      } else {
        this.router.navigate(['/home/amend-invoices']);
      }
    }
  }
  }
  logout(): void {
    this.http.get(ApiUrls.logout).subscribe((res:any)=>{
      localStorage.clear();
      sessionStorage.clear();
      this.cookie.deleteAll()
      // let cookie_names = ['sid','user_id','full_name','system_user']
      // cookie_names.forEach(name=>{
      //   document.cookie=`${name}="sumanth"; expire=2022-08-05T06:43:18.966Z; path=/;`;
      // })
      
      this.router.navigate(['']);
      
      
    })
   
  }
  navigateDashboard() {
    this.router.navigate(['home/dashboard'])
  }

  getPermissions(): void {
    this.docTypes.forEach((each: any) => {
      const queryParams: any = {
        name: each?.name,
        doctype: "DocType"
      };
      this.http.get(ApiUrls.permissions, { params: queryParams }).subscribe((res: any) => {
        let obj = {};
        res['docName'] = each?.name
        this.permissions.push(res);
        localStorage.setItem('permissions', JSON.stringify(this.permissions))
      })
    })
  }


  changePassword(content) {
    this.change_user_details ={}
    this.wrong_password = ''
    this.modal.open(content, {
      centered: true
    })
  }

  check_old_password(e:any){
    if(e.length >= 6){
    this.http.post(ApiUrls.check_old_password,{user:this.loginUser?.email,pwd:e}).subscribe((res:any)=>{
      if(res?.message){
        this.wrong_password = res?.message?.message
      }
    })
    }
  }


  onSubmit(form:NgForm) {
    form.form.markAllAsTouched();
    if(form.valid){
    if (this.change_user_details.new_password) {
      this.http.put(`${ApiUrls.users}/${this.loginUser?.email}`, { new_password: this.change_user_details.new_password , last_password_reset_date: moment(new Date()).format("YYYY-MM-DD") }).subscribe((res: any) => {
        if (res.data) {
          this.toaster.success("Password Changed");
          this.modal.dismissAll();
          this.logout();

        } else {
          this.toaster.error("Failed")
        }
      })
    }
  }
  }

  getNetworkStatus() {
    this.http.get(ApiUrls.networkStatus).subscribe((res: any) => {
      this.networkStatus = res.message
    });
    setInterval(() => {
      this.http.get(ApiUrls.networkStatus).subscribe((res: any) => {
        this.networkStatus = res.message
      });
    }, 60000);
  }

  openNotifications() {
    this.newCount = false;
    const editSacCode = this.modal.open(NotificationsComponent, {
      size: 'md',
      centered: true,
      windowClass: 'modal-sac',
      animation: false
    });
  }

  updateNow() {
    this.router.navigate(['home/bench-logs'])
    this.update = false;
    this.updateUI = false;
  }
  closeUpdate() {
    this.update = false;
    this.updateUI = false;
  }

  clickHeader(updating) {
    this.modal.open(this.updating, { centered: true, size: 'md' })
  }
  showToast(invoice,type) {
    const title = invoice?.message
    const message = invoice?.data?.name
    const obj = {
      printedBy: invoice?.data?.print_by,
      dateOn: invoice?.data?.creation,
      message: invoice?.data?.name,
      type: invoice?.data?.invoice_category
    }
    const obj_pos_checks = {
      printedBy: invoice?.data?.print_by,
      dateOn: invoice?.data?.creation,
      message: invoice?.data?.check_no,
      type: invoice?.data?.doctype
    }

    this.toastRef = this.toaster
      .show(title, message, {
        disableTimeOut: false,
        tapToDismiss: false,
        toastClass: "",
        closeButton: true,
        // positionClass: "bottom-left",
        // @ts-ignore
        buttons: type == "invoice" ? this.toastButtons : null,
        info: type == "invoice" ? obj : obj_pos_checks,
        toastComponent: CustomToastrComponent
      })
      .onAction.subscribe(x => {

        if (x.title == "Print" && invoice?.data?.invoice_file) {
          if (invoice?.data?.irn_generated == "Success") {
            this.fileType(invoice?.data);
          } else {
            this.print(invoice?.data?.invoice_file)
          }
          this.readNotification(invoice?.data);
        }
      });
  };



  print(invoice) {
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = this.apiDomain + invoice;
    document.body.appendChild(iframe);
    if (iframe.src) {
      setTimeout(() => {
        iframe.contentWindow.print();

      })
    }
  }

  readNotification(invoice) {
    this.http.put(`${ApiUrls.resource}/${Doctypes.socNotifications}/${invoice?.name}`, { viewed: 1 }).subscribe((res: any) => {
      if (res) {
        this.newCount = false;
      }
    })
  }

  getNotifications() {
    const queryParams: any = { filters: [] };
    queryParams.fields = JSON.stringify(['name', 'invoice_number', 'creation', 'viewed']);

    this.http.get(`${ApiUrls.resource}/${Doctypes.socNotifications}`, {
      params: {
        fields: JSON.stringify(["count( `tabSocket Notification`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      if (res) {
        queryParams.limit_page_length = res?.data[0]?.total_count
        this.http.get(`${ApiUrls.resource}/${Doctypes.socNotifications}`, {
          params: queryParams
        }).subscribe((response: any) => {
          if (response) {
            this.notificationsList = response?.data
            let xyz = this.notificationsList.filter((res: any) => res.viewed == 0)
            this.newCount = xyz.length > 0 ? true : false;
          }
        })
      }
    })
  }

  async fileType(invoice: any) {
    let qrPng;
    let title = "Invoice"
    if (invoice?.has_credit_items == "Yes" && invoice.invoice_type == "B2B") {
      qrPng = invoice?.credit_qr_code_image;
    } else {
      if (invoice?.invoice_type == "B2B") {
        qrPng = invoice?.qr_code_image;
      }
    }
    if (invoice?.invoice_type == "B2C") {
      qrPng = invoice?.b2c_qrimage;
    }

    let xyz = this.apiDomain + invoice?.invoice_file;
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
        x: parseInt(this.companyDetails.qr_rect_x0),
        y: firstPage.getHeight() - parseInt(this.companyDetails.qr_rect_y0) - parseInt(this.companyDetails.qr_rect_y1),
        width: parseInt(this.companyDetails.qr_rect_x1),
        height: parseInt(this.companyDetails.qr_rect_y1)
      });
      if (invoice?.invoice_type == 'B2B' && invoice?.has_credit_items == "No") {
        const page = this.companyDetails.irn_details_page === 'Last' ? pages[pages.length - 1] : pages[0];

        page.drawText(`IRN : ${invoice.irn_number}    ACK : ${invoice.ack_no}    Date : ${invoice.ack_date}`, {
          x: this.companyDetails?.irn_text_point1,
          y: page.getHeight() - parseInt(this.companyDetails.irn_text_point2),
          // y: this.companyDetails?.irn_text_point2,
          size: 8,
        });
      }

      if (invoice?.invoice_type == 'B2B' && invoice?.has_credit_items == "Yes") {
        const page = this.companyDetails.irn_details_page === 'Last' ? pages[pages.length - 1] : pages[0];

        page.drawText(`IRN : ${invoice.credit_irn_number}    ACK : ${invoice.credit_ack_no}    Date : ${invoice.credit_ack_date}`, {
          x: this.companyDetails?.irn_text_point1,
          y: page.getHeight() - parseInt(this.companyDetails.irn_text_point2),
          // y: this.companyDetails?.irn_text_point2,
          size: 8,
        });
      }

      const pdfDataUri = new Blob([await pdfDoc.save()], { type: "application/pdf" });
      let fileURL = URL.createObjectURL(pdfDataUri);
      // window.open(fileURL);
      this.printQR(fileURL)

      // console.log("Preview File", pdfDataUri)
    } else {
      console.log('QR img not found');
      this.print(invoice?.data?.invoice_file)
    }
  }

  printQR(invoice) {
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = invoice;
    document.body.appendChild(iframe);
    if (iframe.src) {
      setTimeout(() => {
        iframe.contentWindow.print();

      })
    }
  }

  public toggle(type) {
    switch (type) {
      case 'first':
        this.isCollapsed = !this.isCollapsed;
        this.isCollapsedOne = false;
        this.isCollapsedTwo = false;
        break;
      case 'second':
        this.isCollapsedOne = !this.isCollapsedOne;
        this.isCollapsed = false;
        this.isCollapsedTwo = false;
        break;
      default:
        break;
    }
  }
  changeStatusOfCom(event){
    this.bulkUploadExcel = event
  }

  ngOnDestroy() {
    this.destroyEvents.emit(true);
    this.socketService.disconnect();
    let cookie_names = ['sid','user_id','full_name','system_user']
      cookie_names.forEach(name=>{
        document.cookie=`${name}="sumanth"; expire=2022-08-05T06:43:18.966Z; path=/;`;
    })
  }
}

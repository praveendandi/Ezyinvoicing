import { debounceTime, distinctUntilChanged, switchMap, catchError, map } from 'rxjs/operators';
import { Observable, of } from 'rxjs';
import { ApiUrls, Doctypes } from './../../../shared/api-urls';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, ViewChild, ElementRef, ChangeDetectionStrategy } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { environment } from 'src/environments/environment';


@Component({
  selector: 'app-company-details',
  templateUrl: './company-details.component.html',
  styleUrls: ['./company-details.component.scss'],
})
export class CompanyDetailsComponent implements OnInit {
  @ViewChild('fontFileInp') fontFileHtmlRef: ElementRef;
  @ViewChild('form') companyForm: NgForm;
  companyDetails: any = {};
  viewOnly = false;
  filename;
  fileToUpload;
  loginUser: any = {}
  loginUSerRole;
  slabRatesCount: any = {}
  bankDetails: any = {};
  clbsSettings: any = {}
  scSlabRatesCount: any = {}
  syncConfig: any={};
  userName;
  UserSignature: any = {};
  signature_img: any = {}
  signature_pfx: any = {}
  pfx_password;
  showPassword: boolean = false;
  domain = environment.apiDomain
  ezygstSettings: any = {}

  constructor(
    private activatedRoute: ActivatedRoute,
    private route: Router,
    private http: HttpClient,
    private toaster: ToastrService,
    private modal: NgbModal
  ) { }

  ngOnInit(): void {
    this.loginUser = JSON.parse(localStorage.getItem('login'))
    this.loginUSerRole = this.loginUser.rolesFilter.some((each: any) => (each.toLowerCase() == 'ezy-it' || each.toLowerCase() =='ezy-finance' || each.toLowerCase() =='ezy-admin' ))
    console.log(this.loginUSerRole)
    const params = this.activatedRoute.snapshot.params;
    this.viewOnly = !!params.id;
    // if (params.id) {
    //   setTimeout(() => {
    //     this.companyForm.form.disable();
    //   }, 200);
    // }

    if (params.id) {
      this.http.get(ApiUrls.company + '/' + params.id).subscribe((res: any) => {

        this.companyDetails = res.data;
        this.UserSignature = this.companyDetails?.e_signature
        this.signature_img = this.companyDetails?.signature_image
        this.signature_pfx = this.companyDetails?.signature_pfx
        this.pfx_password = this.companyDetails?.pfx_password

        this.slabRatesCount.min = res.data?.slab_12_starting_range;
        this.slabRatesCount.max = res.data?.slab_12_ending_range;

        this.scSlabRatesCount.min = res.data?.sc_slab_12_starting_range;
        this.scSlabRatesCount.max = res.data?.sc_slab_12_end_range

        if(this.companyDetails.ezy_gst_module == '1' ){
          this.getSyncConfig();
        }
        console.log(res, "====", this.scSlabRatesCount.max);
      });
      this.http.get(`${ApiUrls.resource}/${Doctypes.bankDetails}`,{
        params:{
          filters: JSON.stringify([['company','=',params.id]]),
          fields: JSON.stringify(['*'])
        }
      }).subscribe((res:any)=>{
        if(res?.data.length){
          this.bankDetails = res.data[0];
        }
      })
    }
    this.getClbsSettings();
    
    this.getSyncShedule();
  }

  


  handleFileInput(files: File[], field_name) {
    this.filename = files[0].name;
    this.fileToUpload = files[0];
    if (this.fileToUpload) {
      const formData = new FormData();
      formData.append('file', this.fileToUpload, this.fileToUpload.name);
      formData.append('is_private', '1');
      formData.append('folder', 'Home');
      // formData.append('doctype', this.companyDetails.doctype);
      // formData.append('fieldname', field_name);
      formData.append('docname', this.companyDetails.company_code);
      this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
        if (res.message.file_url) {
          if (field_name === 'invoice_reinitiate_parsing_file') {
            this.companyDetails['invoice_reinitiate_parsing_file'] = res.message.file_url
            const formData = new FormData();
            formData.append('doc', JSON.stringify(this.companyDetails));
            formData.append('action', 'Save')
            this.http.post(ApiUrls.fileSave, formData).subscribe((res: any) => {
              this.ngOnInit()
              this.toaster.success('Document Saved')
            });
          }
          if (field_name === 'reinitiate_invoice_api') {
            this.companyDetails['reinitiate_invoice_api'] = res.message.file_url
            const formData = new FormData();
            formData.append('doc', JSON.stringify(this.companyDetails));
            formData.append('action', 'Save')
            this.http.post(ApiUrls.fileSave, formData).subscribe((res: any) => {
              this.ngOnInit()
              this.toaster.success('Document Saved')
            });
          }
          if (field_name === 'invoice_parser_file') {
            this.companyDetails['invoice_parser_file'] = res.message.file_url
            const formData = new FormData();
            formData.append('doc', JSON.stringify(this.companyDetails));
            formData.append('action', 'Save')
            this.http.post(ApiUrls.fileSave, formData).subscribe((res: any) => {
              this.ngOnInit()
              this.toaster.success('Document Saved')
            });
          }
          if (field_name === 'file_upload_api') {
            this.companyDetails['file_upload_api'] = res.message.file_url
            const formData = new FormData();
            formData.append('doc', JSON.stringify(this.companyDetails));
            formData.append('action', 'Save')
            this.http.post(ApiUrls.fileSave, formData).subscribe((res: any) => {
              this.ngOnInit()
              this.toaster.success('Document Saved')
            });
          }

          if (field_name === 'company_logo') {
            this.companyDetails['company_logo'] = res.message.file_url
            const formData = new FormData();
            formData.append('doc', JSON.stringify(this.companyDetails));
            formData.append('action', 'Save')
            this.http.post(ApiUrls.fileSave, formData).subscribe((res: any) => {
              this.ngOnInit()
              this.toaster.success('Document Saved')
            });
          }

          if (field_name === 'custom_e_tax_invoice_logo_image') {
            this.companyDetails['custom_e_tax_invoice_logo_image'] = res.message.file_url
            const formData = new FormData();
            formData.append('doc', JSON.stringify(this.companyDetails));
            formData.append('action', 'Save')
            this.http.post(ApiUrls.fileSave, formData).subscribe((res: any) => {
              this.ngOnInit()
              this.toaster.success('Document Saved')
            });
          }
          if (field_name === 'pms_payment_qr') {
            this.companyDetails['pms_payment_qr'] = res.message.file_url
            const formData = new FormData();
            formData.append('doc', JSON.stringify(this.companyDetails));
            formData.append('action', 'Save')
            this.http.post(ApiUrls.fileSave, formData).subscribe((res: any) => {
              this.ngOnInit()
              this.toaster.success('Document Saved')
            });
          }

          if (field_name === 'custom_e_tax_invoice_footer_image') {
            this.companyDetails['custom_e_tax_invoice_footer_image'] = res.message.file_url
            const formData = new FormData();
            formData.append('doc', JSON.stringify(this.companyDetails));
            formData.append('action', 'Save')
            this.http.post(ApiUrls.fileSave, formData).subscribe((res: any) => {
              this.ngOnInit()
              this.toaster.success('Document Saved')
            });
          }


        }
      })
    }
  }



  handlePfxFileInput(files: File[], field_name) {

    this.filename = files[0].name;
    this.fileToUpload = files[0];
    if (this.fileToUpload) {
      const formData = new FormData();
      formData.append('file', this.fileToUpload, this.fileToUpload.name);
      formData.append('is_private', '1');
      formData.append('folder', 'Home');
      // formData.append('doctype', this.companyDetails?.doctype);
      // formData.append('fieldname', field_name);
      formData.append('docname', this.companyDetails?.company_code);
      this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
        if (res.message.file_url) {
           this.signature_pfx = res.message.file_url

          // if (field_name === 'signature') {
          //   this.companyDetails['signature'] = res.message.file_url
          //   const formData = new FormData();
          //   formData.append('doc', JSON.stringify(this.companyDetails));
          //   formData.append('action', 'Save')
          //   this.http.post(ApiUrls.fileSave, formData).subscribe((res: any) => {
          //     this.ngOnInit()
          //     this.toaster.success('Document Saved')
          //   });
          // }

        }
      })
    }
  }


  handleFileimgInput(files: File[], field_name) {

    this.filename = files[0].name;
    this.fileToUpload = files[0];
    if (this.fileToUpload) {
      const formData = new FormData();
      formData.append('file', this.fileToUpload, this.fileToUpload.name);
      formData.append('is_private', '1');
      formData.append('folder', 'Home');
      // formData.append('doctype', this.companyDetails?.doctype);
      // formData.append('fieldname', field_name);
      formData.append('docname', this.companyDetails?.company_code);
      this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
        if (res.message.file_url) {
           this.signature_img = res.message.file_url

        }
      })
    }
  }


  showHidePassword() {
    this.showPassword = !this.showPassword;
  }

  addSignature(contentSign, userName) {
    this.userName = this.companyDetails?.name
    this.modal.open(contentSign, {
      centered: true
    });
    console.log('=======', this.userName)

  }

  saveSignature(modal) {
    let data={};
    this.signature_pfx ? data['signature_pfx'] = this.signature_pfx:''
    this.pfx_password? data['pfx_password'] = this.pfx_password:''
    this.signature_img? data['signature_image'] = this.signature_img:''

    if (data) {
      this.http.put(ApiUrls.company + `/${this.companyDetails?.name}`, data).subscribe((res: any) => {
        if (res) {
          localStorage.setItem("company", JSON.stringify(res.data))
          // this.ngOnInit();
          this.toaster.success('Saved');
          this.modal.dismissAll()
          // window.location.reload();
        }else {
          this.toaster.error("Failed")
        }
      })
    }
    // this.http.post(`${ApiUrls.resource}/${Doctypes.userSignature}`, data).subscribe((res: any) => {
    //   if (res?.data) {
    //     console.log('=======', this.UserSignature)
    //     this.toastr.success("Updated");
    //     this.UserSignature = res.data;
    //     this.modal.dismissAll();
    //   }
    // })
    // this.http.get(`${ApiUrls.resource}/${Doctypes.userSignature}`, {
    //   params:{
    //     filters:JSON.stringify([['name','=',this.userName]]),
    //     fields:JSON.stringify(['*'])
    //   }
    // }).subscribe((res: any) => {
    //   if (res?.data) {
    //    if(res.data[0]?.signature_image || res.data[0]?.signature_pfx){
    //     this.http.put(`${ApiUrls.resource}/${Doctypes.userSignature}/${res.data[0]?.name}`, data).subscribe((res: any) => {
    //       this.toaster.success("uploaded");
    //       this.UserSignature = res.data;
    //     })
    //    }else{
    //     this.http.post(`${ApiUrls.resource}/${Doctypes.userSignature}`, data).subscribe((res: any) => {
    //       console.log(res?.data)
    //       this.toaster.success("Uploaded");
    //     })
    //    }
    //   }
    // })
  }



  /**
   * Determines whether submit clicked
   * @params form
   */
  onSubmit(form: NgForm): void {
    if (form.value) {
      const formData = new FormData();
      const data = JSON.parse(JSON.stringify(form.value));
      if (data) {
        this.http.put(ApiUrls.company + `/${this.companyDetails?.name}`, data).subscribe((res: any) => {
          if (res) {
            localStorage.setItem("company", JSON.stringify(res.data))
            if(res.data.ezy_gst_module == '1' ){
              this.updateSyncConfig();
            }
            // this.ngOnInit();
            this.toaster.success('Saved');
            window.location.reload();
          }else {
            this.toaster.error("Failed")
          }
        })
      }
     
      this.sheduleUpdate();
      // delete data.font_file;
      // Object.keys(data).forEach(key => {
      //   formData.append(key, data[key]);
      // });
      // const file: File = (this.fontFileHtmlRef?.nativeElement as HTMLInputElement)?.files[0];
      // if (file) {
      //   formData.append('file', file, file.name);
      //   formData.append('doctype', 'company');
      //   formData.append('docname', 'ganesh');
      //   this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
      //     if (res?.message?.file_url) {
      //       data['font_file'] = res?.message?.file_url;
      //       this.saveData(data);
      //     }
      //   });
      // } else {
      //   this.saveData(data);
      // }

    }
  }
  /**
   * Saves company data
   * @param data
   * @returns data
   */
  private saveData(data): void {
    let apiCall;
    if (this.activatedRoute.snapshot.params.id) {
      return;
    } else {
      apiCall = this.http.post(ApiUrls.company, data);
    }
    apiCall.subscribe((res) => {
      console.log(res);
      this.route.navigate(['home/company'], { replaceUrl: true, queryParams: this.activatedRoute.snapshot.queryParams });
    });
  }
  searchProviders = (text$: Observable<string>) => (
    text$.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap((term) => {
        const filters = JSON.stringify([['name', 'like', term]]);
        return this.http.get(ApiUrls.gspApis, {
          params: {
            filters
          }
        }).pipe(
          map((val: any) => (val.data as any[]).map((each) => each.name)),
          catchError(() => {
            return of([]);
          }));
      }
      ),
    ))

  openSlab(slabRates) {
    let modal = this.modal.open(slabRates, { size: 'md', centered: true })
    modal.result.then((res: any) => {
      if (res == 'Success') {
        this.slabRatesCount.min = this.companyDetails?.slab_12_starting_range;
        this.slabRatesCount.max = this.companyDetails?.slab_12_ending_range
      }
    })
  }

  scOpenSlab(scSlabRates) {
    let modal = this.modal.open(scSlabRates, { size: 'md', centered: true })
    modal.result.then((res: any) => {
      if (res == 'Success') {
        this.scSlabRatesCount.min = this.companyDetails?.sc_slab_12_starting_range;
        this.scSlabRatesCount.max = this.companyDetails?.sc_slab_12_end_range
      }
    })
  }


  save_bank_details(){
    this.http.put(`${ApiUrls.resource}/${Doctypes.bankDetails}/${this.bankDetails?.name}`,{
      data:this.bankDetails
    }).subscribe((res:any)=>{
      if(res?.data){
        this.bankDetails = res.data;
      }
    })
  }

  getClbsSettings(){
    this.http.get(`${ApiUrls.clbsSettings}`).subscribe((res:any)=>{
      if(res?.data[0]){
        this.http.get(`${ApiUrls.clbsSettings}/${res?.data[0]?.name}`).subscribe((each:any)=>{
          if(each){
            this.clbsSettings = each?.data;
          }
        })
      }
    })
  }

  getSyncShedule() {
    let queryParams = {
      doctype:Doctypes.EzygstSettings,
      name:Doctypes.EzygstSettings
    }
    this.http.get(`${ApiUrls.getSync}`,{params:queryParams}).subscribe((res: any) => {
      this.ezygstSettings = res.docs[0];
      console.log('========', this.ezygstSettings);
    })
  }

  sheduleUpdate(){
    let obj = {
      doctype:Doctypes.EzygstSettings,
      name:Doctypes.EzygstSettings,
      sync_schedule_time: this.ezygstSettings?.sync_schedule_time,
      creation: this.ezygstSettings?.creation,
      modified: this.ezygstSettings?.modified
    }
    let formData = new FormData()
    formData.append('action','Save')
    formData.append('doc', JSON.stringify(obj));
    this.http.post(`${ApiUrls.fileSave}`,formData).subscribe((res:any)=>{
      if(res?.data){
        this.ezygstSettings = res.docs[0];
        this.toaster.success('Updated')
      }
    })
  }
  

  save_qr_details(){
    console.log(this.clbsSettings?.name)
    if(this.clbsSettings?.name){
    this.http.put(`${ApiUrls.clbsSettings}/${this.clbsSettings?.name}`,{data:this.clbsSettings}).subscribe((res:any)=>{
      if(res?.data){
        this.clbsSettings = res.data;
        this.toaster.success('Updated')
      }
    })
  }else{
    this.clbsSettings['company']=this.companyDetails.company_code
    this.http.post(`${ApiUrls.clbsSettings}`,{data:this.clbsSettings}).subscribe((res:any)=>{
      if(res?.data){
        this.clbsSettings = res.data;
        this.toaster.success('Updated')
      }
    })
  }
  }

  getSyncConfig() {
    this.http.get(`${ApiUrls.getSync}?doctype=${Doctypes.syncConf}&name=${Doctypes.syncConf}`).subscribe((res: any) => {
      this.syncConfig = res.docs[0];
    })

  }

  updateSyncConfig() {

    let form = new FormData()
    form.append('doc',JSON.stringify(this.syncConfig))
    form.append('action','Save')
    this.http.post(`${ApiUrls.fileSave}`,form).subscribe((res: any) => {
      this.syncConfig = res.docs[0];
    })
  }

}

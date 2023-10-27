import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ModalDismissReasons, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-email-settings',
  templateUrl: './email-settings.component.html',
  styleUrls: ['./email-settings.component.scss']
})
export class EmailSettingsComponent implements OnInit {
  loginUser: any = {}
  filename;
  fileToUpload;
  loginUSerRole;
  smtpSettings: any = {}
  emailTemplates: any = {}
  emailAccount: any = {}
  emailTempData: any = {}
  checkTempMethod = false;
  emailTemplatesText: any;
  domain = environment.apiDomain
  closeResult = '';
  use_html: boolean = true
  constructor(
    private http: HttpClient,
    private toaster: ToastrService,
    private modal: NgbModal,
    private modalService: NgbModal
  ) { }

  ngOnInit(): void {
    this.loginUser = JSON.parse(localStorage.getItem('login'))
    this.loginUSerRole = this.loginUser.rolesFilter.some((each: any) => each == 'ezy-IT')
    this.getSmtpData();
    this.getEmailAccountData();
    this.getTemplateData();
  }

  getSmtpData() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.emailDomain}`).subscribe((res: any) => {
      if (res.data) {
        if (res.data.length > 1) {
          let smtpData = res.data[0];
          this.http.get(`${ApiUrls.resource}/${Doctypes.emailDomain}/${smtpData.name}`).subscribe((res: any) => {
            this.smtpSettings = res?.data
          })
        } else {
          this.smtpSettings = {}
        }

      }
    })
  }
  onSubmit(form: NgForm) {
    if (this.smtpSettings?.name) {
      this.http.put(`${ApiUrls.resource}/${Doctypes.emailDomain}/${this.smtpSettings?.name}`, form.value).subscribe((res: any) => {
        // console.log(res)
        if (res) {
          this.smtpSettings = res?.data
          this.toaster.success("Updated")
        }
      })
    } else {
      this.http.post(`${ApiUrls.resource}/${Doctypes.emailDomain}`, form.value).subscribe((res: any) => {
        if (res) {
          this.smtpSettings = res?.data
          this.toaster.success("Added")
        }
      })
    }

  }

  getEmailAccountData() {
    let queryParams: any = { filters: [] };
    queryParams.limit_start = 0
    queryParams.limit_page_length = 20;
    queryParams.order_by = "`tabEmail Account`.`creation` desc"
    queryParams.filters.push(["default_outgoing", "=", 1]);
    queryParams.fields = JSON.stringify(["name", "default_outgoing"]);
    queryParams.filters = JSON.stringify(queryParams.filters);
    this.http.get(`${ApiUrls.resource}/${Doctypes.emailAccount}`, { params: queryParams }).subscribe((res: any) => {
      // console.log(res.data)
      if (res.data) {
        let accountData = res.data[0];
        this.http.get(`${ApiUrls.resource}/${Doctypes.emailAccount}/${accountData.name}`).subscribe((res: any) => {
          this.emailAccount = res?.data
        })
      }
    })
  }

  onSubmitaccountForm(form: NgForm) {
    if (this.emailAccount?.name) {
      this.http.put(`${ApiUrls.resource}/${Doctypes.emailAccount}/${this.emailAccount?.name}`, form.value).subscribe((res: any) => {
        // console.log(res)
        if (res) {
          this.emailAccount = res?.data
          this.toaster.success("Updated")

        }
      })
    } else {
      this.http.post(`${ApiUrls.resource}/${Doctypes.emailAccount}`, form.value).subscribe((res: any) => {
        if (res) {
          this.emailAccount = res?.data
          this.toaster.success("Added")
        }
      })
    }
  }


  getTemplateData() {
    let queryParams: any = { filters: [] };
    queryParams.fields = JSON.stringify(["name", "subject", "response_html", "response", "use_html", "email_client_banner"]);
    this.http.get(`${ApiUrls.resource}/${Doctypes.emailTemplates}`, { params: queryParams }).subscribe((res: any) => {
      // console.log(res.data)
      if (res.data.length != 0) {
        this.emailTemplates = res.data;
      }
    })

  }

  addNewTemp(emailtemplate) {
    this.emailTempData = {}
    this.checkTempMethod = false;
    let modal = this.modal.open(emailtemplate, { size: 'lg', centered: true })
  }
  emailForm(form: NgForm, modal) {

    // let dataObj = {
    //   name: form.value.template_name,
    //   subject: form.value.subject,
    //   response: form.value.message,
    //   use_html: form.value.use_html ==true? 1 : 0,
    //   owner: this.loginUser?.name
    // }

    let dataObj = form.value.use_html == true ?
      {
        name: form.value.template_name,
        subject: form.value.subject,
        response_html: form.value.message,
        use_html: 1,
        owner: this.loginUser?.name,
        email_client_banner: this.emailTempData.email_client_banner
      } :
      {
        name: form.value.template_name,
        subject: form.value.subject,
        response: form.value.emailTemplatesText,
        use_html: 0,
        owner: this.loginUser?.name,
        email_client_banner: this.emailTempData.email_client_banner
      }
    // console.log(dataObj)
    if (this.checkTempMethod) {
      this.http.put(`${ApiUrls.resource}/${Doctypes.emailTemplates}/${dataObj.name}`, dataObj).subscribe((res: any) => {
        // console.log(res)
        if (res) {
          modal.dismiss("close")
          this.getTemplateData();
          this.toaster.success("Updated")
        }
      })
    } else {
      this.http.post(`${ApiUrls.resource}/${Doctypes.emailTemplates}`, dataObj).subscribe((res: any) => {

        // console.log(res)
        if (res) {
          modal.dismiss("close")
          this.getTemplateData()
          this.toaster.success("Added")
        }
      })
    }
  }

  deleteTemp(item) {
    if (!window.confirm(`Are you sure to delete ${item.name} Template? `)) {
      return null;
    } else {
      this.http.delete(`${ApiUrls.resource}/${Doctypes.emailTemplates}/${item.name}`).subscribe((res: any) => {
        if (res?.message == 'ok') {
          this.getTemplateData()
          this.toaster.success(`${item.name} Template is deleted`)
        }
      })
    }
  }
  editTemp(item, emailtemplate) {
    this.emailTempData = item;
    this.checkTempMethod = true;
    this.emailTempData.email_client_banner
    let modal = this.modal.open(emailtemplate, { size: 'lg', centered: true })

  }
  open(content) {
    // let modal = this.modal.open(emailtemplate, { size: 'lg', centered: true })
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title', size: 'lg', centered: true }).result.then(
      (result) => {
        this.closeResult = `Closed with: ${result}`;
      },
      (reason) => {
        this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
      },
    );
  }

  private getDismissReason(reason: any): string {
    if (reason === ModalDismissReasons.ESC) {
      return 'by pressing ESC';
    } else if (reason === ModalDismissReasons.BACKDROP_CLICK) {
      return 'by clicking on a backdrop';
    } else {
      return `with: ${reason}`;
    }
  }

  // onSelectFile(event) {
  //   if (event.target.files && event.target.files[0]) {
  //     var reader = new FileReader();
  //     reader.readAsDataURL(event.target.files[0]); 
  //     reader.onload = (event) => { 
  //       this.email_client_banner = event.target.result;
  //     }
  //   }

  // }

  succesToaster() {
    this.toaster.success("Updated")
  }

  handleFileInput(files: File[], field_name) {
    this.filename = files[0].name;
    // debugger
    this.fileToUpload = files[0];
    if (this.fileToUpload) {
      const formData = new FormData();
      formData.append('file', this.fileToUpload, this.fileToUpload.name);
      formData.append('is_private', '1');
      formData.append('folder', 'Home');
      // formData.append('docname', this.emailTempData?.email_client_banner);
      this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
        // console.log(res)
        if (res.message.file_url) {
          if (field_name === 'email_client_banner') {
            this.emailTempData['email_client_banner'] = res.message.file_url
            console.log(this.emailTempData['email_client_banner'])
            const formData = new FormData();
            formData.append('doc', JSON.stringify(this.emailTempData));
            formData.append('action', 'Save')
            // this.http.post(ApiUrls.fileSave, formData).subscribe((res: any) => {
            //   this.ngOnInit()
            //   this.toaster.success('Document Saved')
            // });
          }

        }
      })
    }
  }
}


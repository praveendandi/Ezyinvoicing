import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';

@Component({
  selector: 'app-email-settings',
  templateUrl: './email-settings.component.html',
  styleUrls: ['./email-settings.component.scss']
})
export class EmailSettingsComponent implements OnInit {
  loginUser: any = {}
  loginUSerRole;
  smtpSettings: any = {}
  emailTemplates: any = {}
  emailAccount: any = {}
  emailTempData: any = {}
  checkTempMethod = false;
  emailTemplatesText:any;


  use_html:boolean=true
  constructor(
    private http: HttpClient,
    private toaster: ToastrService,
    private modal: NgbModal
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
    queryParams.fields = JSON.stringify(["name", "subject", "response_html", "response","use_html"]);
    this.http.get(`${ApiUrls.resource}/${Doctypes.emailTemplates}`, { params: queryParams }).subscribe((res: any) => {
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
   let dataObj =form.value.use_html ==true?
   {
      name: form.value.template_name,
      subject: form.value.subject,
      response_html: form.value.message,
      use_html: 1,
      owner: this.loginUser?.name
    }:
    {
        name: form.value.template_name,
        subject: form.value.subject,
        response: form.value.emailTemplatesText,
        use_html:  0,
        owner: this.loginUser?.name
      }

    if (this.checkTempMethod) {
      this.http.put(`${ApiUrls.resource}/${Doctypes.emailTemplates}/${dataObj.name}`, dataObj).subscribe((res: any) => {
        if (res) {
          modal.dismiss("close")
          this.getTemplateData();
          this.toaster.success("Updated")
        }
      })
    } else {
      this.http.post(`${ApiUrls.resource}/${Doctypes.emailTemplates}`, dataObj).subscribe((res: any) => {
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
    let modal = this.modal.open(emailtemplate, { size: 'lg', centered: true })
  }
}

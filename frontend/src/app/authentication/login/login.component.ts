import { ApiUrls } from './../../shared/api-urls';
import { Component, EventEmitter, OnDestroy, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgForm } from '@angular/forms';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { IToastButton } from 'src/app/shared/custom/custom-toastr/custom-toastr.component';
import { SocketService } from 'src/app/shared/services/socket.service';
import { takeUntil } from 'rxjs/operators';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit,OnDestroy {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  toastRef;
  toastButtons: IToastButton[] = [
    {
      id: "1",
      title: "view jobs 1"
    },
    {
      id: "2",
      title: "view jobs 2"
    }
  ];

  constructor(
    private router: Router,
    private http: HttpClient,
    private toastr: ToastrService,
    private socketService : SocketService,
    private modalService : NgbModal
  ) { }

  ngOnInit(): void {
    sessionStorage.removeItem("SelItem")
    // this.socketService.connectMe();
    // this.socketService.newInvoice.pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
    //   if (!res) { return }
    //   if (res.message.type === 'system_reload') {
    //    window.location.reload();
    //   }
    // })
  }

  /**
   * Determines whether submit on
   * @params form
   */
  onSubmit(form: NgForm): void {
    if (form.valid) {
      const formData = new FormData();
      formData.append('usr', form.value.username);
      formData.append('pwd', form.value.password);
      formData.append('cmd', 'login');
      formData.append('device', 'desktop');
      const data = {
        usr: form.value.username,
        pwd: form.value.password,
      };
      this.http.post(ApiUrls.login, data).subscribe((res: any) => {
        this.getCompanyData();
        this.getTotalCount(res?.full_name, form.value)
        // localStorage.setItem('login',JSON.stringify(res))
        // this.router.navigate(['/home']);
        // this.toastr.success('successfully logged in ')
      }, (err) => {
        form.form.setErrors({ error: err.error.message });
      });
    } else {
      form.form.markAllAsTouched();
    }
  }


  getTotalCount(userName, formData): void {
    this.http.get(`${ApiUrls.users}`, {
      params: {
        fields: JSON.stringify(["count( `tabUser`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {

      this.getUSerList(res.data[0].total_count, userName, formData);
    })
  }
  getUSerList(count, userName, formData): void {
    const queryParams: any = { filters: [] };
    queryParams.filters.push(['full_name', 'like', `%${userName}%`]);
    let re = /\S+@\S+\.\S+/;
    let checkUserName = re.test(formData.username)
    console.log(checkUserName)
    if (checkUserName) {
      queryParams.filters.push(['email', 'like', `%${formData.username}%`]);
    } else {
      queryParams.filters.push(['username', 'like', `%${formData.username}%`]);
    }

    queryParams.limit_page_length = count;
    queryParams.filters = JSON.stringify(queryParams.filters);
    this.http.get(`${ApiUrls.users}`, {
      params: queryParams
    }).subscribe((res: any) => {
      if (res?.data) {
        this.http.get(`${ApiUrls.users}/${res?.data[0]?.name}`).subscribe((userData: any) => {
          if (userData?.data) {
            let roles = userData.data.roles.map((each) => each.role);
            roles = roles.filter(each => each.includes('ezy'));
            userData.data['rolesFilter'] = roles;
            localStorage.setItem('login', JSON.stringify(userData?.data))
            this.router.navigate(['/home']);
            this.toastr.success('successfully logged in ')
          }
        })
      }

    })


  }

  getCompanyData(){
    this.http.get(ApiUrls.company).subscribe((res: any) => {
      let company = res.data[0];
      if (company) {
        this.http.get(ApiUrls.company + '/' + company?.name).subscribe((res: any) => {
          // this.companyDetails = res.data;
          localStorage.setItem("company", JSON.stringify(res.data))
        });
      }
    })
  }

  ngOnDestroy(): void {
    this.modalService.dismissAll();
  }
}

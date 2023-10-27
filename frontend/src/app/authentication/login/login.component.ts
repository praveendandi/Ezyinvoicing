import { ApiUrls } from './../../shared/api-urls';
import { AfterViewInit, Component, ElementRef, EventEmitter, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgForm } from '@angular/forms';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { IToastButton } from 'src/app/shared/custom/custom-toastr/custom-toastr.component';
import { SocketService } from 'src/app/shared/services/socket.service';
import { takeUntil } from 'rxjs/operators';
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { promise } from 'protractor';
import moment from 'moment';
import { CookieService } from 'ngx-cookie-service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit,OnDestroy,AfterViewInit {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  @ViewChild('content')usersModel: ElementRef | undefined;

  toastRef;
  userData:any;
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
  new_password:any = ''
  login_resp:any = {}
  login_form_data:any = {}
  show_password = false;
  confirmPassword:any= ''
  change_user_details:any = {}
  wrong_password:any ;
  constructor(
    private router: Router,
    private http: HttpClient,
    private toastr: ToastrService,
    private socketService : SocketService,
    private modalService : NgbModal,
    private cookie : CookieService
  ) { }

  ngAfterViewInit():void{
    let cookie_names = ['sid','user_id','full_name','system_user']
    cookie_names.forEach(name=>{
      document.cookie=`${name}=; expire=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    })
  }


  ngOnInit(): void {
    
    // document.cookie = 'sid=; user_id:"":path=/;'
    // this.socketService.connectMe();
    // this.socketService.newInvoice.pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
    //   if (!res) { return }
    //   if (res.message.type === 'system_reload') {
    //    window.location.reload();
    //   }
    // })
    // let xyz = document.cookie
    //   console.log("============",window.document.cookie)
    //   this.cookie.deleteAll();
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
        this.login_resp = res?.full_name;
        this.login_form_data = form.value;
        this.getCompanyData()
        this.getUSerList()
      }, (err) => {
        console.log(err.error.exc_type, "============ ", err.error.exception, " ++++ ",err.error._server_message        )
        if(err.error.exc_type == "SecurityException"){
          form.form.setErrors({ error: err.error.exception.split(":").pop() });
        }else{        
          form.form.setErrors({ error: err.error.message });
        }
      });
    } else {
      form.form.markAllAsTouched();
    }
  }

  resetPAssword(form: NgForm){   
    if (form.valid) {
      this.login_form_data = form.value;
      this.http.post(ApiUrls.reset_password,{
        "user":form.value.username,
        "doctype":"User",
        "fieldname":"password"
      }).subscribe((res:any) =>{
        if(res?.message?.message == 'New login force to reset'  || res?.message?.remaining_days == 0){
          this.userData = res?.message
          this.wrong_password = ""
           this.modalService.open(this.usersModel,{size:'md',centered:true,backdrop:'static'})
        }else if(res?.message?.message == 'Old login'){
          this.show_password = true;
        }else{
          this.toastr.error("Invalid User")
        }
      })  
    } 
  }


  check_old_password(e:any){
    if(e.length >= 6){
    this.http.post(ApiUrls.check_old_password,{user:this.userData.user,pwd:e}).subscribe((res:any)=>{
      if(res?.message){
        this.wrong_password = res?.message?.message
      }
    })
    }
  }

  // getTotalCount(userName, formData): void {
  //   this.http.get(`${ApiUrls.users}`, {
  //     params: {
  //       fields: JSON.stringify(["count( `tabUser`.`name`) AS total_count"])
  //     }
  //   }).subscribe((res: any) => {

  //     this.getUSerList(res.data[0].total_count, userName, formData);
  //   })
  // }
  getUSerList(): void {
    const queryParams: any = { filters: [] };
    queryParams.filters.push(['full_name', 'like', `%${this.login_resp}%`]);
    let re = /\S+@\S+\.\S+/;
    let checkUserName = re.test(this.login_form_data.username)
    console.log(checkUserName)
    if (checkUserName) {
      queryParams.filters.push(['email', 'like', `%${this.login_form_data.username}%`]);
    } else {
      queryParams.filters.push(['username', 'like', `%${this.login_form_data.username}%`]);
    }
    queryParams.filters = JSON.stringify(queryParams.filters);
    this.http.get(`${ApiUrls.users}`, {
      params: queryParams
    }).subscribe((res: any) => {
      if (res?.data) {
        this.http.get(`${ApiUrls.users}/${res?.data[0]?.name}`).subscribe((userData: any) => {
          if (userData?.data) {
           
            let roles = userData.data.roles.map((each) => each.role);
            roles = roles.filter(each => each.includes('ezy-'));
            userData.data['rolesFilter'] = roles;
            localStorage.setItem('login', JSON.stringify(userData?.data))
            this.router.navigate(['/home/dashboard']);
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
    let cookie_names = ['sid','user_id','full_name','system_user']
      cookie_names.forEach(name=>{
        document.cookie=`${name}="sumanth"; expire=2022-08-05T06:43:18.966Z; path=/;`;
      })
  }

  onSubmitResetPwd(form:NgForm){
    console.log(this.login_form_data)
    form.form.markAllAsTouched();
    if (form.valid) {
      this.http.post(`${ApiUrls.initial_password}`,{
        "email": this.userData?.user,
        "last_password_reset_date": moment(new Date()).format("YYYY-MM-DD"),
        "new_password": form.value.new_password,
        "old_pwd": form.value.old_password  
      }).subscribe((res:any)=>{
        console.log(res)
        if(res?.message?.success){
          this.toastr.success("Password Changed");
          this.modalService.dismissAll();
          this.show_password = true;
        }else{
          this.toastr.error("Failed")
        }
      })
      // this.http.put(`${ApiUrls.users}/${this.userData.d}`, { new_password: form.value.new_password , last_password_reset_date: moment(new Date()).format("YYYY-MM-DD") }).subscribe((res: any) => {
      //   if (res?.data) {
      //     this.toastr.success("Password Changed");
      //     this.modalService.dismissAll();
      //     this.show_password = true;   
      //   } else {
      //     this.toastr.error("Failed")
      //   }
      // })
    }
  }
}

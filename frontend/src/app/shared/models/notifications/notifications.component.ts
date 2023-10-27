import { HttpClient } from '@angular/common/http';
import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { Router } from '@angular/router';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ApiUrls, Doctypes } from '../../api-urls';

@Component({
  selector: 'app-notifications',
  templateUrl: './notifications.component.html',
  styleUrls: ['./notifications.component.scss']
})
export class NotificationsComponent implements OnInit {
  notificationsList = [];
  constructor(
    private activeModal: NgbActiveModal,
    private http: HttpClient,
    private router : Router
  ) { }

  ngOnInit(): void {
    this.getNotifications()
  }

  getNotifications() {
    const queryParams: any = { filters: [] };
    queryParams.fields = JSON.stringify(['name', 'invoice_number',  'guest_name', 'confirmation_number', 'room_number', 'invoice_type','invoice_category','print_by','creation','viewed','record_type']);
      
    this.http.get(`${ApiUrls.resource}/${Doctypes.socNotifications}`,{
      params: {
        fields: JSON.stringify(["count( `tabSocket Notification`.`name`) AS total_count"])
      }}).subscribe((res: any) => {
      if (res) {
        console.log(res)
        queryParams.limit_page_length = 150;
        this.http.get(`${ApiUrls.resource}/${Doctypes.socNotifications}`,{
          params: queryParams}).subscribe((response: any) => {
          if (response) {
            this.notificationsList = response?.data
            let xyz = this.notificationsList.filter((res: any) => res.viewed == 0)
            setTimeout(()=>{
              xyz.map((each:any)=>{
                this.readNotification(each)
              })
            },10000)
          }
        })
      }
    })   
  }

  readNotification(invoice) {
    this.http.put(`${ApiUrls.resource}/${Doctypes.socNotifications}/${invoice?.name}`, { viewed: 1 }).subscribe((res: any) => {
      if (res) {
        
      }
    })
  }
  navigateDetails(each){
    this.router.navigate(['home/invoice-details/'+each.name])
  }

  closeModal() {
    this.activeModal.close();
  }

  deleteOne(each){
    this.http.delete(`${ApiUrls.resource}/${Doctypes.socNotifications}/${each.name}`).subscribe((res:any)=>{
      if(res.message){
        this.getNotifications()
      }
    })
  }
  deleteAll(){
    this.http.get(ApiUrls.clearNotifications).subscribe((res:any)=>{
      if(res?.message?.success){
        this.getNotifications()
      }
    })
  }
}

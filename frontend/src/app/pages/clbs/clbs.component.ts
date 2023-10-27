import { Component, OnInit } from '@angular/core';
import { SocketService } from 'src/app/shared/services/socket.service';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-clbs',
  templateUrl: './clbs.component.html',
  styleUrls: ['./clbs.component.scss'],
  styles : [':host{background: #fff;height:100vh;display:block;}']
})
export class ClbsComponent implements OnInit {
  hideShow = false;
  company:any = {}
  domain = environment.apiDomain
  constructor(
    private socketService : SocketService
  ) { }

  ngOnInit(): void {
    this.socketService.connectMe();
    this.company = JSON.parse(localStorage.getItem('company'));
  }

  toggle(type:any){
    if(type === 'list'){
     this.hideShow = true
    }
    if(type === 'grid'){
     this.hideShow = false
    }
   }

}

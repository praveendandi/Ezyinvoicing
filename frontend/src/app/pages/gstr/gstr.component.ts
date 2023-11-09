import { Component, OnInit } from '@angular/core';
import { SocketService } from 'src/app/shared/services/socket.service';

@Component({
  selector: 'app-gstr',
  templateUrl: './gstr.component.html',
  styleUrls: ['./gstr.component.scss']
})
export class GstrComponent implements OnInit {

  constructor(
    private socketService : SocketService
  ) { }

  ngOnInit(): void {
    this.socketService.connectMe();
  }

}

import { Injectable, OnInit } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { BehaviorSubject, Subject } from 'rxjs';
@Injectable({
  providedIn: 'root'
})
export class SocketService implements OnInit {
  public newReCon = new Subject()
  public newReConProcessing = new Subject()
  public deleteReCon = new Subject()
  public sync_invoices = new Subject()
  public sync_sac_hsn_codes = new Subject()
  public sync_taxpayers = new Subject()
  public sync_completed = new Subject()
  readonly newInvoice = new BehaviorSubject(null);
  readonly isContactAdded = new BehaviorSubject(null);
  readonly newPosChecks = new BehaviorSubject(null);
  readonly summaryData = new BehaviorSubject(null);
  private company;
  constructor(private socket: Socket) {


  }
  ngOnInit() {

  }
  connectMe() {
    setInterval(() => {
      console.log(this.socket.ioSocket.connected);
    }, 2000)
    console.log('connectMe invoked');
    this.socket.on('connection', () => {
      console.log('socket connected')
    })
    this.socket.on('connect-me', () => {
      console.log('socket connect-me event')
    })
    this.socket.on('message', (data) => {
      console.log('socket message: ', data)
      this.newInvoiceFun(data);
      // this.newInvoice.next(null);

      switch (data?.message.message) {
        case 'POS Checks':
          this.newPosChecks.next(data?.message);
          break;
        case 'Invoices Sync':
          this.sync_invoices.next(data?.message);
          break;
        case 'Item Sync':
          this.sync_sac_hsn_codes.next(data?.message);
          break;
        case 'Taxpayer Sync':
          this.sync_taxpayers.next(data?.message);
          break;
        case 'Sync Completed':
          this.sync_completed.next(data?.message);
          break;
        case 'Delete Recon':
          this.deleteReCon.next(data?.message);
          break;
        case 'Create Recon':
          this.newReCon.next(data?.message);
          break;
        case 'Recon Processing':
          this.newReConProcessing.next(data?.message);
          break;

      }
    })

    this.socket.connect();
  }


  newInvoiceFun(data) {
    this.company = JSON.parse(localStorage.getItem('company'));
    if (this.company.company_code == data.message.company) {
      this.newInvoice.next(data);
    } else {
      this.summaryData.next(data)
    }

  }


  disconnect() {
    this.socket.removeAllListeners();
    this.socket.disconnect();
  }
}

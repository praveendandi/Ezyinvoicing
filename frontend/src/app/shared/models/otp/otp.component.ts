import { Component, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-otp',
  templateUrl: './otp.component.html',
  styleUrls: ['./otp.component.scss']
})
export class OtpComponent implements OnInit {

  otp:any;
  constructor(
    private modal: NgbActiveModal
  ) { }

  ngOnInit(): void {
  }

  close(){
    this.modal.close()
  }

  otpEntered(e:any){
    // console.log(e.target.value)
    if(e.target.value.length == 6){
      // console.log("=======",e.target.value)
      this.modal.close(e.target.value)
    }
  }
}

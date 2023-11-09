import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-faqs',
  templateUrl: './faqs.component.html',
  styleUrls: ['./faqs.component.scss'],
  styles: [':host {background:#f9f9f9; display:block}']
})
export class FaqsComponent implements OnInit {

  userData;

  constructor(private router: Router) { }

  ngOnInit(): void {
    const localData = localStorage.getItem('login')
    this.userData = JSON.parse(localData);
  }

  logoNav() {
    if (this.userData) {
      this.router.navigate(['/home/dashboard']);
    } else {
      this.router.navigate(['/'])
    }
  }

  userManagement() {
    if (this.userData) {
      this.router.navigate([]).then(result => {  window.open('/home/users', '_blank'); });
    } else {
      this.router.navigate(['/'])
    }
  }

  permissions() {
    if (this.userData ) {
      this.router.navigate([]).then(result => {  window.open('/home/permissions', '_blank'); });
    } else {
      this.router.navigate(['/'])
    }
  }

  invoices() {
    if (this.userData) {
      this.router.navigate([]).then(result => {  window.open('/home/invoices', '_blank'); });
    } else {
      this.router.navigate(['/'])
    }
  }

  sac(){
    if (this.userData) {
      this.router.navigate([]).then(result => {  window.open('/home/sac-hsn-codes', '_blank'); });
    } else {
      this.router.navigate(['/'])
    }
  }


}

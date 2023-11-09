import { Location } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-gstr2-reconciliation',
  templateUrl: './gstr2-reconciliation.component.html',
  styleUrls: ['./gstr2-reconciliation.component.scss']
})
export class Gstr2ReconciliationComponent implements OnInit {

  constructor(
    private location : Location,
    private router : Router
  ) { }

  ngOnInit(): void {
  }

  gotoBack(){
    this.location.back()
  }
  openFullTable(){
    const url = this.router.serializeUrl(
      this.router.createUrlTree(['home/gstr2-data'])
    )
    window.open(url, '_blank');
  }
}

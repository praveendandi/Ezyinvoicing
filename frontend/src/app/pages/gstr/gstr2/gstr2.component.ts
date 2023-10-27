import { Location } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { Router } from '@angular/router';
import { ApiUrls } from 'src/app/shared/api-urls';
import Stepper from 'bs-stepper';


@Component({
  selector: 'app-gstr2',
  templateUrl: './gstr2.component.html',
  styleUrls: ['./gstr2.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class Gstr2Component implements OnInit {
  rows:any = [
    {id: 1, heading: "All other ITC - supplies from Registered Persons", GSTR3B: "4(A)(5)", ITax: "3,45,33,320.00", CTax: "3,45,33,320.00", STax: "3,45,33,320.00", Cess: "3,45,33,320.00", showDetail: false  },
    {id: 2, heading: "Inward supplies from ISD", GSTR3B: "4(A)(5)", ITax: "3,45,33,320.00", CTax: "3,45,33,320.00", STax: "3,45,33,320.00", Cess: "3,45,33,320.00", showDetail: false},
    {id: 3, heading: "Inward Supplies liable for reverse charge", GSTR3B: "4(A)(5)", ITax: "3,45,33,320.00", CTax: "3,45,33,320.00", STax: "3,45,33,320.00", Cess: "3,45,33,320.00", showDetail: false},
    {id: 4, heading: "Import of Goods", GSTR3B: "4(A)(5)", ITax: "3,45,33,320.00", CTax: "3,45,33,320.00", STax: "3,45,33,320.00", Cess: "3,45,33,320.00", showDetail: false},
  ];

  registers:any = [
    {id: 1, heading: "Supplies from registered persons (B2B)", Documents: "100", TaxValue: "3,33,33,333.33", TaxAmount: "3,33,33,333.33", showDetail: false  },
    {id: 2, heading: "Deemed Exports (DE)", Documents: "100", TaxValue: "3,33,33,333.33", TaxAmount: "3,33,33,333.33", showDetail: false  },
    {id: 3, heading: "SEZWP", Documents: "100", TaxValue: "3,33,33,333.33", TaxAmount: "3,33,33,333.33", showDetail: false  },
    {id: 4, heading: "SEZWOP", Documents: "100", TaxValue: "3,33,33,333.33", TaxAmount: "3,33,33,333.33", showDetail: false  },

  ]

  array: any = [
    length = 1
  ]

  ViewDetail() {
    this.router.navigate(['/purchase-register'])
  }

  
  active: any;
  years: any = [];
  filters:any ={
    selectedYear :'',
    selectedMonth : ''
  }
  monthNames = [{name:"January",id:'01'},{name:"February",id:'02'} ,{name:"March",id:'03'} ,{name:"April",id:'04'} ,{name:"May",id:'05'} ,{name: "June",id:'06'},
  {name:"July",id:'07'} ,{name:"August",id:'08'} ,{name:"September",id:'09'} ,{name:"October",id:'10'} ,{name:"November",id:'11'} ,{name:"December",id:'12'} ];
  days:any;
  dates:any = {from:'',to:''}
  b2bInvoicesData:any;
  private stepper: Stepper;

  constructor(
    private router: Router,
    private location: Location,
    private http : HttpClient
  ) { }

  next() {
    this.stepper.next();
  }

  onSubmit() {
    return false;
  }

  ngOnInit(): void {

    this.stepper = new Stepper(document.querySelector('#stepper1'), {
      linear: false,
      animation: true
    })

    let year = new Date().getFullYear();
    this.filters.selectedYear = year;
    for (var i = 0; i < 5; i++) {
      let previousYear = year - i;
      this.years.push(previousYear);
    }
    let month = new Date().getMonth()+1
    this.filters.selectedMonth = month < 10 ? `0${month}`:month;
    if(month && year){
     let days = this.daysInMonth(month,year);
     if(days){
       this.dates.from = `${this.filters.selectedYear}-${this.filters.selectedMonth}-01`;
       this.dates.to = `${this.filters.selectedYear}-${this.filters.selectedMonth}-${days}`
     }
    }
   this.getb2bTotalData();
    
  }

  daysInMonth (month:any, year:any) {
    return this.days = new Date(year, month, 0).getDate();
}
  gotoBack() {
    // this.location.back()
    this.router.navigate(['home/dashboard'])
  }

  changeSelect(e:any,type:any){
    let days = this.daysInMonth(this.filters.selectedMonth,this.filters.selectedYear);
    this.dates.from = `${this.filters.selectedYear}-${this.filters.selectedMonth}-01`;
    this.dates.to = `${this.filters.selectedYear}-${this.filters.selectedMonth}-${days}`
  }
  
  getb2bTotalData(){
    this.http.post(ApiUrls.gstr2Ab2bData,{data:this.dates}).subscribe((res:any)=>{
      if(res.message.data){
        this.b2bInvoicesData = res.message.data;
      }
    })
  }
}

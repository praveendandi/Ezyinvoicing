import { Component, OnInit } from '@angular/core';
import { ApiUrls } from 'src/app/shared/api-urls';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-purchase-register',
  templateUrl: './purchase-register.component.html',
  styleUrls: ['./purchase-register.component.scss']
})
export class PurchaseRegisterComponent implements OnInit {
  monthNames = [{name:"January",id:'01'},{name:"February",id:'02'} ,{name:"March",id:'03'} ,{name:"April",id:'04'} ,{name:"May",id:'05'} ,{name: "June",id:'06'},
  {name:"July",id:'07'} ,{name:"August",id:'08'} ,{name:"September",id:'09'} ,{name:"October",id:'10'} ,{name:"November",id:'11'} ,{name:"December",id:'12'} ];
  days:any;
  dates:any = {from:'',to:''}
  filters:any ={
    selectedYear :'',
    selectedMonth : ''
  }
  years: any = [];
  b2bInvoicesData:any;

  registers:any = [
    { heading: "1230MDOWJTT90TO", trade: "CaratredRed Technolgies pvt ltd", InvoiceType: "B2B", InvoiceNumber: "12340040404-1", InvoiceDate: '12-02-2022', TaxableValue: '3,33,33,333.33', IntergratedTax: '3,33,33,333.33', CentralTax: '3,33,33,333.33', UTTax: '3,33,33,333.33', Cess: '3,33,33,333.33'   },
    { heading: "1230MDOWJTT90TO", trade: "CaratredRed Technolgies pvt ltd", InvoiceType: "B2B", InvoiceNumber: "12340040404-1", InvoiceDate: '12-02-2022', TaxableValue: '3,33,33,333.33', IntergratedTax: '3,33,33,333.33', CentralTax: '3,33,33,333.33', UTTax: '3,33,33,333.33', Cess: '3,33,33,333.33'   },
    { heading: "1230MDOWJTT90TO", trade: "CaratredRed Technolgies pvt ltd", InvoiceType: "B2B", InvoiceNumber: "12340040404-1", InvoiceDate: '12-02-2022', TaxableValue: '3,33,33,333.33', IntergratedTax: '3,33,33,333.33', CentralTax: '3,33,33,333.33', UTTax: '3,33,33,333.33', Cess: '3,33,33,333.33'   },
    { heading: "1230MDOWJTT90TO", trade: "CaratredRed Technolgies pvt ltd", InvoiceType: "B2B", InvoiceNumber: "12340040404-1", InvoiceDate: '12-02-2022', TaxableValue: '3,33,33,333.33', IntergratedTax: '3,33,33,333.33', CentralTax: '3,33,33,333.33', UTTax: '3,33,33,333.33', Cess: '3,33,33,333.33'   },
  ]

  array: any = [
    length = 1
  ]

  
  constructor(
    private http : HttpClient
  ) { }

  ngOnInit(): void {
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

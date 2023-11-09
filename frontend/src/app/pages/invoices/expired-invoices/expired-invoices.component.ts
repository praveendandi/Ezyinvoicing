import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import moment from 'moment';
import { ApiUrls } from 'src/app/shared/api-urls';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-expired-invoices',
  templateUrl: './expired-invoices.component.html',
  styleUrls: ['./expired-invoices.component.scss']
})
export class ExpiredInvoicesComponent implements OnInit {

  years: any = []
  selectedDate : any = 'All';
  selectedMonth: any;
  selectedYear: any;
  companyDetails: any;
  invoiceList: any;
  invoiceSearchObj:any = {};
  apiDomain = environment.apiDomain;

  days_in_a_month:any;
  constructor(
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.selectedMonth = new Date().getMonth()
    this.selectedYear = new Date().getFullYear()
    if (this.selectedMonth + 1 <= 9) {
      this.selectedMonth = this.selectedMonth ? `${0}${this.selectedMonth + 1}` : `${0}${this.selectedMonth + 1}`;
    } else {
      this.selectedMonth = this.selectedMonth ? `${this.selectedMonth + 1}` : `${this.selectedMonth + 1}`;
    }

    this.getYear()
    this.getInvoices()
  }

  getInvoices() {
    this.invoiceList =[] 
    let start_date; let end_date;
    this.days_in_a_month = [...Array(this.daysInMonth(this.selectedMonth, this.selectedYear)).keys()]
    let days_per_month = this.daysInMonth(this.selectedMonth, this.selectedYear)
    let date_expiry: any = moment(moment(new Date()).subtract(7, 'd').format('YYYY-MM-DD'))
    date_expiry = moment(date_expiry).format('YYYY-MM-DD')
    let last_date = this.selectedYear + '-' + this.selectedMonth + '-' + days_per_month

    if(this.selectedDate != 'All'){
      start_date = this.selectedYear + '-' + this.selectedMonth + '-' + this.selectedDate
      end_date = this.selectedYear + '-' + this.selectedMonth + '-' + this.selectedDate
    }else{ 
      start_date = this.selectedYear + '-' + this.selectedMonth + '-' + '01'
      end_date = last_date < date_expiry ? last_date : date_expiry
    }
   
    const queryParams: any = { filters: [] };
    queryParams.filters.push(['invoice_type', "like", "B2B"], ['irn_generated', 'in', ["Pending", "Error"]], ["Invoices", "invoice_date", "Between", [start_date, end_date]])
    queryParams.fields = JSON.stringify(['*']);
    queryParams.filters = JSON.stringify(queryParams.filters);
    queryParams.limit_page_length = 'None'
    queryParams.order_by = "`tabInvoices`.`invoice_date` desc";
    this.http.get(ApiUrls.invoices, { params: queryParams }).subscribe((res: any) => {
      if(res?.data.length){
        this.invoiceList = res?.data
        this.invoiceList = res?.data.filter((each:any)=>{

          let today_date: any = moment(each?.invoice_date).format('YYYY-MM-DD')
          let date_expiry: any = this.companyDetails?.e_invoice_missing_start_date ? moment(this.companyDetails?.e_invoice_missing_start_date).format('YYYY-MM-DD') : null
          if (this.companyDetails?.e_invoice_missing_date_feature && today_date >= date_expiry) {
            let date_expiry: any = moment(moment(each?.invoice_date).add(7, 'd').format('YYYY-MM-DD'))
            date_expiry = moment(date_expiry).format('YYYY-MM-DD')
            each['expiry_date'] = moment(date_expiry).format('YYYY-MM-DD')
            return each;
          }
          
        })  
      }
    })
  }

  daysInMonth(month, year) {
    return new Date(year, month, 0).getDate();
  }
  getYear() {
    var currentYear = new Date().getFullYear()
    var startYear = 2022;
    for (var i = startYear; i <= currentYear; i++) {
      this.years.push(startYear++);
    }
    return this.years;
  }

  onDateFilterMonthChange() {
    try {
      this.getInvoices()
    } catch (err) {
      console.log(err)
    }

  }
  
  downloadReport(){
    this.http.post(ApiUrls.report_for_invoices,{report_type : 'expired',month:this.selectedMonth,year:this.selectedYear}).subscribe((res:any)=>{
      if(res?.message?.success){
        window.open(`${this.apiDomain}${res?.message?.file_path}`, "_blank");
      }
    })
  }
}

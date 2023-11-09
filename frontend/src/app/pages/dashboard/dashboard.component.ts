import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { ApiUrls } from '../../shared/api-urls';
import * as Moment from 'moment';
import { JsonPipe } from '@angular/common';
import {DateToFilter} from 'src/app/shared/date-filter'
@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {

  invoices = {
    pending: 0,
    success: 0,
    cancelled: 0
  }

  credits = {
    pending: 0,
    success: 0,
    cancelled: 0
  }

  debits = {
    pending: 0,
    success: 0,
    cancelled: 0
  }
  sacTotalCount = 0
  dateFilters = "Last Week"

  invoiceFilter = {
    time_interval: 'Daily',
    timespan: 'Last Week'
  }
  sacHsnFilter = {
    time_interval: 'Daily',
    timespan: 'Last Week'
  }

  summariesDateFilter ={
    start_date:'',
    end_date:''
  }
  lineChartData = []
  barChartData = []
  options
  showXAxis = true;
  showYAxis = true;
  gradient = false;
  showLegend = true;
  showXAxisLabel = false;
  xAxisLabel = 'Date';
  showYAxisLabel = false;
  yAxisLabel = 'HSN Codes';
  showGridLines = true;
 
  maxXAxisTickLength = 10;


  view: any[] = [520, 300];
  colorScheme = {
    domain: ['#2E5BFF']
  };

  sacHsnSummaries = [];
  creditNoteSummaries = [];
  creditSumFilter= 'Last Week';
  sacHsnSumFilter='Last Week'
  constructor(
    private route: Router,
    private http: HttpClient,
    private activatedParams: ActivatedRoute
  ) { }
  ngOnInit(): void {
    this.getInvoices();
    this.getBarChartData();
    this.getLineChartData();
    this.getSacSummaries();
    this.getcreditSummaries();

    // let updateStorage = localStorage.getItem('update')
    // if (updateStorage) {

    // } else {
    //   this.checkUpdates();
    // }
  }

  getInvoices(): void {
    const pendingParams: any = { filters: [['irn_generated', '=', 'Pending']] };
    pendingParams.filters.push(new DateToFilter('Invoices', this.dateFilters).filter);
    pendingParams.filters = JSON.stringify(pendingParams.filters)
    pendingParams.fields = JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"])
    const pending = this.http.get(`${ApiUrls.invoices}`, { params: pendingParams });

    const successParams: any = { filters: [['irn_generated', '=', 'Success']] };
    successParams.filters.push(new DateToFilter('Invoices', this.dateFilters).filter);
    successParams.filters = JSON.stringify(successParams.filters);
    successParams.fields = JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"])
    const success = this.http.get(`${ApiUrls.invoices}`, { params: successParams });

    const cancelledParams: any = { filters: [['irn_generated', '=', 'Cancelled']] };
    cancelledParams.filters.push(new DateToFilter('Invoices', this.dateFilters).filter);
    cancelledParams.filters = JSON.stringify(cancelledParams.filters)
    cancelledParams.fields = JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"])
    const cancel = this.http.get(`${ApiUrls.invoices}`, { params: cancelledParams });

    const creditsPending: any = { filters: [["Invoices", "has_credit_items", "=", "Yes"], ["Invoices", "irn_generated", "=", "Pending"]] }
    creditsPending.filters.push(new DateToFilter('Invoices', this.dateFilters).filter);
    creditsPending.filters = JSON.stringify(creditsPending.filters);
    creditsPending.fields = JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"]);
    const crePending = this.http.get(`${ApiUrls.invoices}`, { params: creditsPending });

    const creditsSuccess: any = { filters: [["Invoices", "has_credit_items", "=", "Yes"], ["Invoices", "irn_generated", "=", "Success"]] }
    creditsSuccess.filters.push(new DateToFilter('Invoices', this.dateFilters).filter);
    creditsSuccess.filters = JSON.stringify(creditsSuccess.filters)
    creditsSuccess.fields = JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"])
    const creSuccess = this.http.get(`${ApiUrls.invoices}`, { params: creditsSuccess });

    const creditsCancel: any = { filters: [["Invoices", "has_credit_items", "=", "Yes"], ["Invoices", "irn_generated", "=", "Cancelled"]] }
    creditsCancel.filters.push(new DateToFilter('Invoices', this.dateFilters).filter);
    creditsCancel.filters = JSON.stringify(creditsCancel.filters)
    creditsCancel.fields = JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"])
    const creCancel = this.http.get(`${ApiUrls.invoices}`, { params: creditsCancel });

    const sacTotalCount = this.http.get(`${ApiUrls.sacHsn}`, {
      params: {
        fields: JSON.stringify(["count( `tabSAC HSN CODES`.`name`) AS total_count"]),
      }
    });

    forkJoin([pending, success, cancel, crePending, creSuccess, creCancel, sacTotalCount]).subscribe((res: any) => {
      const [pend, suc, can, crePending, creSuccess, creCancel, sacTotalCount] = res;
      this.invoices.pending = pend.data[0].total_count;
      this.invoices.success = suc.data[0].total_count;
      this.invoices.cancelled = can.data[0].total_count;
      this.credits.pending = crePending.data[0].total_count;
      this.credits.success = creSuccess.data[0].total_count;
      this.credits.cancelled = creCancel.data[0].total_count;
      this.sacTotalCount = sacTotalCount.data[0].total_count;
    })

  }


  getLineChartData(): void {
    const invoiceData = new FormData();
    invoiceData.append('chart_name', 'Invoice Chart');
    // invoiceData.append('filters', JSON.stringify([["Invoices", "state_code", "=", "7", false]]));
    invoiceData.append('time_interval', this.invoiceFilter.time_interval);
    invoiceData.append('timespan', this.invoiceFilter.timespan);
    // invoiceData.append('from_date', '');
    // invoiceData.append('to_date', '');
    this.http.post(ApiUrls.dashboard, invoiceData).subscribe((res: any) => {
      const invoiceLineData = res
      let dataObj = {}
      // let x = invoiceLineData.message.labels;
      // var i = x.length;
      // while (i--) {
      //   (i + 3) % 3 !== 0 && x.splice(i, 1, ' ');
      // }
      // console.log("+++++++++",x);
      let items = invoiceLineData.message.datasets[0].values.map((id, index) => {
        return {
          name: invoiceLineData.message.labels[index],
          value: invoiceLineData.message.datasets[0].values[index]
        }
      });
      // console.log("====",items)
      if (items) {
        dataObj["name"] = invoiceLineData.message.datasets[0].name;
        dataObj["series"] = items;
      }
      this.lineChartData.push(dataObj);
    });
  }

  getBarChartData(): void {
    const sacHsnData = new FormData();
    sacHsnData.append('chart_name', 'Sac Hsn codes');
    sacHsnData.append('filters', JSON.stringify([]));
    sacHsnData.append('time_interval', this.sacHsnFilter.time_interval);
    sacHsnData.append('timespan', this.sacHsnFilter.timespan);
    // sacHsnData.append('from_date', '');
    // sacHsnData.append('to_date', '');
    this.http.post(ApiUrls.dashboard, sacHsnData).subscribe((res: any) => {
      const sacHsnBarData = res;
      let sacObj = sacHsnBarData.message.datasets[0].values.map((id, index) => {
        return {
          name: sacHsnBarData.message.labels[index],
          value: sacHsnBarData.message.datasets[0].values[index]
        }
      });
      this.barChartData = sacObj
      // console.log(this.barChartData)

    });
  }
  onDateFilterChange() {
    this.getInvoices();
    // this.getCharts();
  }

  onDateFilterChange1() {
    this.lineChartData = [];
    this.getLineChartData()
  }

  onDateFilterChange2() {
    this.barChartData = [];
    this.getBarChartData();
  }

  onDateFilterChangeSummary(){
    this.getSacSummaries();
  }
  getSacSummaries():void{
  let xyz = new DateToFilter('sacSummaries', this.dateFilters).filter;
   let dataObj = {start_date:xyz[3][0],end_date:xyz[3][1]}
    this.http.post(ApiUrls.sacSummaries,dataObj).subscribe((res:any)=>{
      if(res?.message?.success){
        this.sacHsnSummaries = res?.message?.data
        this.sacHsnSummaries = this.sacHsnSummaries.filter((each:any)=>each.cgst!==0 && each.sgst !== 0)
      }
    })
  }
  onDateFilterCreditSummary():void{
    this.getcreditSummaries()
  }
  getcreditSummaries():void{
    let xyz = new DateToFilter('creditSummaries', this.dateFilters).filter;
   let dataObj = {start_date:xyz[3][0],end_date:xyz[3][1]}
   this.http.post(ApiUrls.creditSummaries,dataObj).subscribe((res:any)=>{
     if(res?.message?.success){
      this.creditNoteSummaries = res?.message?.data
     }
   })
  }

  // getUpdates(){
  //   this.route.navigate(['home/bench-logs'])
  // }

  // checkUpdates(): void {
  //   let checkUpdate, data;
  //   this.http.get(ApiUrls.checkUpdates).subscribe((res: any) => {
  //     if (res.message.success) {
  //       data = res?.message.message[0];
  //     }
  //     this.http.get(`https://gitlab.caratred.com/api/v4/projects/329/repository/branches/stable-version?private_token=PCyLiE1o6xAMUzgR6Wir`).subscribe((res: any) => {
  //       if (res) {
  //         this.branchUpdate = res;
  //         console.log(this.branchUpdate)
  //         checkUpdate = res?.commit?.id;
  //         this.update = (data == checkUpdate) ? true : false;
  //         localStorage.setItem('update', JSON.stringify(this.update))
          
  //       }
  //     })
  //   })
  // }
}

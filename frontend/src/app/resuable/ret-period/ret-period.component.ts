import { Component, EventEmitter, OnInit } from '@angular/core';
import { takeUntil } from 'rxjs/operators';
import { MonthYearService } from 'src/app/shared/services/month-year.service';

@Component({
  selector: 'app-ret-period',
  templateUrl: './ret-period.component.html',
  styleUrls: ['./ret-period.component.scss']
})
export class RetPeriodComponent implements OnInit {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  yearsList:any = [];
  monthList:any =[];
  month:any = '';
  year:any = '';
  
  constructor(
    private yearService: MonthYearService
  ) { }

  ngOnInit(): void {
    this.yearService.years.pipe(takeUntil(this.destroyEvents))
      .subscribe((data) => this.yearsList = data);

    this.yearService.months.pipe(takeUntil(this.destroyEvents))
      .subscribe((data) => this.monthList = data);
      
     let storageDates :any = JSON.parse(localStorage.getItem('dateFilters'));
      if(storageDates?.month && storageDates?.year){
        this.month = storageDates.month;
        this.year = storageDates.year;
      }else{

        const d = new Date();
        d.setMonth(d.getMonth() - 1);
        let month: any = d.toLocaleString('default', { month: 'long' });
        month = d.getMonth() + 1;
        let year: any = d.getFullYear();
        this.month = month;
        this.year = year;      

        this.setDates(month,year);
      }

      // var lastDayOfMonth = new Date(this.year, this.month+1, 0);
      // console.log("====",lastDayOfMonth)
    

    this.yearService.setSelectedYear(this.year);
    this.yearService.setSelectedMonth(this.month);
  }


  selectMonthYear(e:any, type:string ){
    if (type === 'month' && e) {
      this.month = e;
      this.setDates(e,null)
      this.yearService.setSelectedMonth(this.month);
    }
    if (type === 'year' && e) {
      this.year = e;
      this.setDates(null,e)
      this.yearService.setSelectedYear(this.year);
    }
  }
  setDates(month,year){
    let objDates ={
      month:month?month:this.month, year:year?year : this.year
    }
    localStorage.setItem('dateFilters',JSON.stringify(objDates));
  }
}

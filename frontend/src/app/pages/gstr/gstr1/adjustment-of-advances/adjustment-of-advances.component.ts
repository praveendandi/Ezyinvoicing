import { Component, EventEmitter, OnDestroy, OnInit } from '@angular/core';
import { takeUntil } from 'rxjs/operators';
import { MonthYearService } from 'src/app/shared/services/month-year.service';

@Component({
  selector: 'app-adjustment-of-advances',
  templateUrl: './adjustment-of-advances.component.html',
  styleUrls: ['./adjustment-of-advances.component.scss']
})
export class AdjustmentOfAdvancesComponent implements OnInit,OnDestroy {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();

  year:any;
  month:any;
  constructor(
    private yearService: MonthYearService
    ) { }

  ngOnInit(): void {

    this.yearService.getSelectedYear().pipe(takeUntil(this.destroyEvents)).subscribe((res:any)=>{
      if(!res){return;}
    this.year = res;
    if(this.year != '' && this.month != ''){
    
    }
    })
    this.yearService.getSelectedMonth().pipe(takeUntil(this.destroyEvents)).subscribe((res:any)=>{
      if(!res){return;}
    this.month = res;
    if(this.year != '' && this.month != ''){
      
      }
    })
  }


  ngOnDestroy(){
    this.destroyEvents.next();
    this.destroyEvents.unsubscribe();
  }
}

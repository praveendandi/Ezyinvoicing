import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnDestroy, OnInit } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { takeUntil } from 'rxjs/operators';
import { UploadExcelFileComponent } from 'src/app/shared/models/upload-excel-file/upload-excel-file.component';
import { MonthYearService } from 'src/app/shared/services/month-year.service';

@Component({
  selector: 'app-advance-received',
  templateUrl: './advance-received.component.html',
  styleUrls: ['./advance-received.component.scss']
})
export class AdvanceReceivedComponent implements OnInit,OnDestroy {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  year:any;
  month:any;
  constructor(
    private http : HttpClient,
    private Modal : NgbModal,
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


  uploadExcelFile(){
    let modal = this.Modal.open(UploadExcelFileComponent,{size: 'xl', centered: true, windowClass: 'custom-modal'})
  }

  ngOnDestroy(){
    this.destroyEvents.next();
    this.destroyEvents.unsubscribe();
  }
}

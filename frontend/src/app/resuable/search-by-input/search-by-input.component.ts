import { Component, EventEmitter, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { takeUntil } from 'rxjs/operators';
import { SearchByInputService } from './search-by-input.service';

@Component({
  selector: 'app-search-by-input',
  templateUrl: './search-by-input.component.html',
  styleUrls: ['./search-by-input.component.scss']
})
export class SearchByInputComponent implements OnInit, OnDestroy {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();

  searchCond = '';
  searchBy = '';
  searchCondList = [];
  constructor(
    private inputService: SearchByInputService,
    private activatedRoute: ActivatedRoute
  ) { }

  ngOnInit() {
    this.activatedRoute?.queryParams?.subscribe((res: any) => {
      if (!res?.search) { return }
      let data = res?.search ? JSON.parse(res?.search) : '';
      this.searchBy = data?.searchBy || ''
      this.searchCond = data?.searchCond || '';
    })


    this.inputService.getSearchByList().pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
      if (!res) { return; }
      this.searchCondList = res;
    })
    if (!this.searchCond) {
      this.searchCond = this.searchCondList[0];
      this.inputService.setSearchType(this.searchCond);
    }

    // this.inputService.getInputValue().pipe(takeUntil(this.destroyEvents)).subscribe((res:any)=>{
    //   if(!res){return;}
    //   this.searchBy = res;
    // })
    // this.inputService.getSearchType().pipe(takeUntil(this.destroyEvents)).subscribe((res:any)=>{
    //   if(!res){return;}
    //   this.searchCond = res;
    // })

  }

  selectSearchCond(type: string) {
    this.searchCond = type;
    this.searchBy = ''
    this.inputService.setSearchType(this.searchCond);
    this.inputService.setInputValue(this.searchBy);
  }
  OnchangeValue(e: any) {
    this.searchBy = e;
    this.inputService.setInputValue(this.searchBy);
  }
  ngOnDestroy() {
    this.destroyEvents.next();
    this.destroyEvents.unsubscribe();
  }
}

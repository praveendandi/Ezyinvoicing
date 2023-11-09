import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SearchByInputService {

  inputValue = new BehaviorSubject<any>(null);
  searchType = new BehaviorSubject<any>(null);
  searchByList = new BehaviorSubject<any>([]);

  constructor() { }

  setInputValue(data: any) {
    this.inputValue.next(data);
  }

  getInputValue() {
    return this.inputValue.asObservable();
  }

  setSearchType(data: any) {
    this.searchType.next(data);
  }

  getSearchType() {
    return this.searchType.asObservable();
  }

  setSearchByList(data: any) {
    this.searchByList.next(data);
  }

  getSearchByList() {
    return this.searchByList.asObservable();
  }
}

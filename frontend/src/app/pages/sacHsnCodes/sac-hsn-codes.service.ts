import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';

@Injectable({
  providedIn: 'any'
})
export class SacHsnCodesService {
  details = Array(5).fill({
    sNo: 1, name: 'Room Charges SAC - 996311', description: 'Room Charges SAC - 996311', cGst: '9%', sGst: '9%', createdOn: '2days ago'
  });
  constructor() { }

  /**
   * Gets code details
   * @returns code details
   */
  getCodeDetails(): Observable<any> {
    return of(this.details);
  }

  /**
   * Gets particular code details
   * @params id
   * @returns particular code details
   */
  getParticularCodeDetails(id: number): any {
    // tslint:disable-next-line: triple-equals
    return this.details.find(each => each.sNo == id);
  }
}

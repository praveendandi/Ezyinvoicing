import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PaymentTypeService {
  details = Array(5).fill({
    sNo: 1, name: 'American Express', paymentType: 'Card', company: 'JP-2059', createdOn: '2days ago'
  });
  constructor() { }

  /**
   * Getpayments details
   * @returns details
   */
  getpaymentDetails(): Observable<any> {
    return of(this.details);
  }

  /**
   * Gets particular payment details
   * @params id
   * @returns particular payment details
   */
  getParticularPaymentDetails(id: number): any {
    // tslint:disable-next-line: triple-equals
    return this.details.find(each => each.sNo == id);
  }
}

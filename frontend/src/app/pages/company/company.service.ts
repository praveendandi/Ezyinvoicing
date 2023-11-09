import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';

@Injectable({ providedIn: 'any' })

export class CompanyService {
    details = Array(5).fill({
        sNo: 1, name: 'Mohan Chaitanya', companyName: 'Jaypee Greens',
        tradeName: 'Jay Prakash Associate Limited', legalName: 'Jay Prakash Associate Limited', createdOn: '2days ago'
    });
    constructor() { }

    /**
     * Gets company details
     * @returns company details
     */
    getCompanyDetails(): Observable<any> {
        return of(this.details);
    }

    /**
     * Gets particular company details
     * @params id
     * @returns particular company details
     */
    getParticularCompanyDetails(id: number): any {
        // tslint:disable-next-line: triple-equals
        return this.details.find(each => each.sNo == id);
    }
}

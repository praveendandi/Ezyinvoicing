import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, throwError } from 'rxjs';

@Injectable({
    providedIn: 'root'
})

export class MonthYearService {


    months = new BehaviorSubject<any>([]);
    years = new BehaviorSubject<any>([]);

    selectedYear = new BehaviorSubject<any>(null);
    selectedMonth = new BehaviorSubject<any>(null);

    constructor() {
        this.monthsFun();
    }

    monthsFun() {
        let startYear = new Date("2020").getFullYear();
        let currentYear: any = new Date().getFullYear();
        const month = ["January","February","March","April","May","June","July","August","September","October","November","December"];
        const monthInt = [1,2,3,4,5,6,7,8,9,10,11,12];
        const months = [
          {short:1,long:'January',mmm_format:'Jan'},
          {short:2,long:'February',mmm_format:'Feb'},
          {short:3,long:'March',mmm_format:'Mar'},
          {short:4,long:'April',mmm_format:'Apr'},
          {short:5,long:'May',mmm_format:'May'},
          {short:6,long:'June',mmm_format:'Jun'},
          {short:7,long:'July',mmm_format:'Jul'},
          {short:8,long:'August',mmm_format:'Aug'},
          {short:9,long:'September',mmm_format:'Sep'},
          {short:10,long:'October',mmm_format:'Oct'},
          {short:11,long:'November',mmm_format:'Nov'},
          {short:12,long:'December',mmm_format:'Dec'}]
        this.months.next(months);
        let yearList:any = []
        for (let i: any = startYear; i <= currentYear; i++) {
            yearList.push(i);
            yearList.reverse();
            this.years.next(yearList)
        }
    }

    setSelectedYear(data:any){
        this.selectedYear.next(data);
    }

    getSelectedYear(){
        return this.selectedYear.asObservable();
    }

    setSelectedMonth(data:any){
        this.selectedMonth.next(data);
    }

    getSelectedMonth(){
        return this.selectedMonth.asObservable();
    }
}

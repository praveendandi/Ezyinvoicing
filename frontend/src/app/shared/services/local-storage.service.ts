import { BehaviorSubject, Observable } from 'rxjs';
import { Injectable } from '@angular/core';


export const Storekeys = {
  LOGIN : 'login'
}

@Injectable({
  providedIn: 'root'
})
export class LocalStorageService {
  subjectNames: string[] = [];
  protected subjects: { [key: string]: BehaviorSubject<any> } = {};

  constructor() {
    try {
      // const storageCallback = (val: StorageEvent) => {
      //   console.log(val);
      //   /** to remove entire users */
      //   if (val.storageArea.length <= 0) {
      //     this.removeAll();
      //   } else if (this.subjects) {
      //     for (const each of Object.keys(val.storageArea)) {
      //       try {
      //         if (this.subjects[each]) {
      //           this.subjects[each].next(this.parseData(val.storageArea[each]));
      //         } else {
      //           this.subjects[each] = new BehaviorSubject(this.parseData(val.storageArea[each]));
      //         }
      //       } catch (e) {
      //         console.log(e, 'error');
      //       }

      //     }
      //   }
      // };
      // window.addEventListener('storage', storageCallback);
    } catch (E) {
      console.log(E, 'error in storage callback ')
    }

  }

  public removeItem(fileName:any) {
    return localStorage.removeItem(fileName);
  }

  select(key: string, defaultValue: any = null, decodeJwt = false): BehaviorSubject<any> {
    try {
      if (this.subjects.hasOwnProperty(key)) {
        return this.subjects[key];
      }

      if (!window.localStorage.getItem(key) && defaultValue) {
        if (typeof defaultValue == 'string') {
          window.localStorage.setItem(key, defaultValue);
        } else {
          window.localStorage.setItem(key, JSON.stringify(defaultValue));
        }
      }
      let value;
      const temp = window.localStorage.getItem(key);
      if (decodeJwt && temp && typeof temp === 'string') {
        // value = jwt_decode(temp);
      } else if (temp != null && temp) {
        value = JSON.parse(window.localStorage.getItem(key) || '');
      } else {
        value = defaultValue;
      }
      this.subjects[key] = new BehaviorSubject(value);
      return this.subjects[key];
    } catch (e) {
      this.subjects[key] = new BehaviorSubject(null);
      return this.subjects[key];
      // console.log(e, 'error in select method in local storage')
    }
  }
  getRawValue(key: string) {
    return window.localStorage.getItem(key);
  }

  setVal(key: string, value: any, isJwt = false): void {
    try {
      if (typeof value == 'string') {
        window.localStorage.setItem(key, value);
      } else {
        window.localStorage.setItem(key, JSON.stringify(value));
      }
      // if (isJwt && typeof value === 'string') {
      //   value = jwt_decode(value);
      // }
      if (this.subjects.hasOwnProperty(key)) {
        this.subjects[key].next(value);
      } else {
        this.subjects[key] = new BehaviorSubject(value);
      }
    } catch (e) {
      console.log(e, 'error in setVal method in local storage');
    }

  }

  remove(key: string): void {
    window.localStorage.removeItem(key);
    if (this.subjects.hasOwnProperty(key)) {
      this.subjects[key].next(null);
    }
  }
  removeAll() {
    Object.keys(window.localStorage).forEach((each: string) => {
      if (this.subjects[each]) {
        this.subjects[each].next(null);
      }
      window.localStorage.removeItem(each);
    });

  }
}

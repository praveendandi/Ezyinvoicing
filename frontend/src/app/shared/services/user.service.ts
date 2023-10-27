import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { distinctUntilChanged } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private currentUserSubject = new BehaviorSubject<any>({});
  public currentUser = this.currentUserSubject.asObservable().pipe(distinctUntilChanged());

  public doctypePermSubject = new BehaviorSubject<any>({});
  public doctypePerm = this.doctypePermSubject.asObservable().pipe(distinctUntilChanged());

  constructor(
    private http: HttpClient,
    private router: Router
  ) { }

  setUser(user) {
    // console.log('new user', user.docinfo.permissions);
    this.currentUserSubject.next(user);
  }

 
    // const temp = data.reduce((prev,nxt)=> {
    //   const keys = Object.keys(nxt);
    //   keys.forEach((each)=>{
    //   prev[each] = prev[each] || 0;
    //     prev[each] = nxt[each] >prev[each] ? nxt[each]: prev[each];
    //   });
    //   return prev;
    // },{});
    // console.log(temp);

  
  docTypePermissions(data){
    console.log("user docType ====",data)
        this.doctypePermSubject.next(data);
  }
}

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, Resolve, RouterStateSnapshot } from '@angular/router';
import { from, Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { ApiUrls } from './shared/api-urls';
import { UserService } from './shared/services/user.service';

@Injectable()
export class PermissionResolver implements Resolve<any> {

   constructor(
       private http : HttpClient,
       private userService : UserService
   ) { }

   resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<any> {
    console.log("Route ====",route);
    console.log("State ====",state)
    const queryParams : any ={};
    queryParams.doctype = route.data.docType
    this.http.get(ApiUrls.perDoctype,{params:queryParams}).subscribe((res:any)=>{
        console.log(res)
        // this.userService.docPermissions(res)
    })
    return ;
    // return this.http.get(ApiUrls.permissions).pipe()
}
   
}
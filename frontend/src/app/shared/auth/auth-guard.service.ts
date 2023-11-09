import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { UserService } from '../services/user.service';
import { ActivatedRouteSnapshot, CanActivate, CanActivateChild, Router, RouterStateSnapshot } from '@angular/router';
import { ApiUrls } from '../api-urls';
import { ToastrService } from 'ngx-toastr';
@Injectable({
  providedIn: 'root'
})
export class AuthGuardService implements CanActivate, CanActivateChild {

  permissions: any = []
  userRole: any = []
  constructor(
    private http: HttpClient,
    private userService: UserService,
    private toastr: ToastrService,
    private router: Router
  ) { }


  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    let user = JSON.parse(localStorage.getItem('login'))
    // console.log("Auth service ====", route, state.url);
    if (route.routeConfig.path == '') {
      if (user) {
        this.router.navigate(['/home'])
        return false;
      }
      return true;
    } else {
      if (!user) {
        this.router.navigate([''])
        return false;
      }
      return true;
    }


  }

  canActivateChild(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    return this.userDocAccess(route);
  }

  userDocAccess(route) {
    this.permissions = JSON.parse(localStorage.getItem('permissions'));
    this.userRole = JSON.parse(localStorage.getItem('UserRoles'));
    let user = JSON.parse(localStorage.getItem('login'))
    if (user?.full_name !== 'Administrator') {
      if (route.data.docType) {
        // console.log("r===",route.data.docType,)
        let filteredDoc = this.permissions?.find((item: any) => item.docName == route.data.docType)
        // console.log("r===",filteredDoc?.docs[0]?.permissions)
        if (filteredDoc?.docs[0]?.permissions.length > 0) {
          let filteredRoles = filteredDoc?.docs[0]?.permissions.filter((ele) => this.userRole.find((each) => each === ele.role))
          // console.log("filteredRoles ===",filteredRoles, this.userRole)
          if (filteredRoles.length) {
            const temp = filteredRoles.reduce((prev, nxt) => {
              const keys = Object.keys(nxt);
              keys.forEach((each) => {
                prev[each] = prev[each] || 0;
                prev[each] = nxt[each] > prev[each] ? nxt[each] : prev[each];
              });
              return prev;
            }, {});
            // this.userService.docTypePermissions(temp)
            localStorage.setItem("checkPermissions", JSON.stringify(temp))
            return true
          } else {
            console.log(" ======= No permissions")
            this.toastr.error("No Permissions")
            return false;
          }

        } else {
          // console.log("No permissions")
          this.toastr.error("No Permissions");
          return false;
        }
      } else {
        return true;
      }
    } else {
      return true;
    }


  }


}

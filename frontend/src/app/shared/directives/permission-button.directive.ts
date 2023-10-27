import { Directive, ElementRef, Input, NgModule, OnInit } from '@angular/core';
import { UserService } from '../services/user.service';

@Directive({
  selector: '[appPermissionButton]'
})
export class PermissionButtonDirective implements OnInit {
  @Input("moduleType") moduleType: string;
  @Input("accessType") accessType: string;
  permissions: any = {}
  constructor(
    private elementRef: ElementRef,
    private userService: UserService
  ) { }

  ngOnInit() {
    // this.elementRef.nativeElement.style.display = "none";
    // this.checkDocLevelAccess();
    // setTimeout(()=>{this.checkAccess()},5000)

    // console.log("moduleType ====",this.moduleType)
    // console.log("accessType ======",this.accessType)
    // if(this.moduleType === "docType"){
      this.checkDocLevelAccess()
    // }else{
      // this.checkAccess()
    // }
  }

  checkAccess(): void {
    this.userService.currentUser.subscribe((res: any) => {
      // console.log("Doctype Access ===================",res)
      if (res?.docinfo?.permissions) {
        let accessControls = res?.docinfo?.permissions
        // console.log("Controls Access ===================",accessControls)
        let check = accessControls.hasOwnProperty(this.accessType)
        // console.log("disable ====",this.accessType)
        if (check) {
          this.elementRef.nativeElement.disabled = accessControls[this.accessType] > 0 ? false : true;
          // console.log(this.elementRef.nativeElement.disabled,"hello")
        }
        
      }
    })
  }

  checkDocLevelAccess(): void {
    // this.userService.doctypePerm.subscribe((res: any) => {
    //   console.log("Doctype Access", res)
    //   let check = res.hasOwnProperty(this.accessType)
    //   console.log("disable ====", this.accessType, check)
    //   if (check) {
    //     this.elementRef.nativeElement.disabled = res[this.accessType] > 0 ? false : true;
    //   }
    // })
    this.permissions = JSON.parse(localStorage.getItem("checkPermissions"))
    let check = this.permissions?.hasOwnProperty(this.accessType)
    if (check) {
      this.elementRef.nativeElement.disabled = this.permissions[this.accessType] > 0 ? false : true;
      // console.log(this.elementRef.nativeElement.disabled,"hello", this.accessType)
    }
  }
}

@NgModule({
  declarations: [PermissionButtonDirective],
  exports: [PermissionButtonDirective]
})
export class PermissionButtonDirectiveModule { }
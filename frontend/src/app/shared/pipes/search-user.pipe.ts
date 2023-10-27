import { NgModule, Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'searchUser'
})
export class SearchUserPipe implements PipeTransform {

  transform(value: [], email?:any , role?:any, username?:any): any {
    if (!value) return null;   

    if (value && value.length) {
      return value.filter((item: any) => {        

        if (email) {
            return item?.email?.toLowerCase()?.includes(email.toLowerCase());
        }
        if (role ) {
            return item?.role?.toLowerCase()?.includes(role.toLowerCase());
        }
        if(username){
          return item?.username?.toLowerCase().includes(username.toLowerCase())
        }       
        
        return true;
    })
    }else {
      return value;
  }

   
  }
  

}
@NgModule ({
  declarations: [SearchUserPipe],
  exports : [SearchUserPipe]
})

export class SearchUserPipeModule {}


@Pipe({
  name: 'searchPermission'
})
export class SearchPermissionPipe implements PipeTransform {

  transform(value: [], module?:any,route?:any): any {
    if (!value) return null;   

    if (value && value.length) {
      return value.filter((item: any) => {        

        if (module) {
            return item?.module?.toLowerCase()?.includes(module.toLowerCase());
        }   
        if (route ) {
          return item?.select_route?.toLowerCase()?.includes(route.toLowerCase());
      }   
        
        return true;
    })
    }else {
      return value;
  }

   
  }
  

}
@NgModule ({
  declarations: [SearchPermissionPipe],
  exports : [SearchPermissionPipe]
})

export class SearchPermissionPipeModule {}
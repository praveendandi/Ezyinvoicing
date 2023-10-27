import { Directive, forwardRef, NgModule } from '@angular/core';
import { AbstractControl, NG_VALIDATORS, Validators } from '@angular/forms';

@Directive({
  selector: '[appValidateGST]',
  providers: [
    { provide: NG_VALIDATORS, useExisting: forwardRef(() => ValidateGSTDirective), multi: true }
]
})
export class ValidateGSTDirective implements Validators {

  constructor() { }
  validate(c: AbstractControl): { [key: string]: any } {
    let v = c.value;
    if(!v){
      return c.errors;
    }else if(this.validateGST(v)){
      return null;
    }else{
      return ({gst:'Invalid GST'});
    }
}
validateGST(data) {
  if (data) {
    // const gstinregx =/[0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[Zz1-9A-Ja-j]{1}[0-9a-zA-Z]{1}/;
    // const uinregx = /[0-9]{4}[A-Z]{3}[0-9]{5}[UO]{1}[N][A-Z0-9]{1}/;
    // const nrid =/[0-9]{4}[a-zA-Z]{3}[0-9]{5}[N][R][0-9a-zA-Z]{1}/;
    // const oidar_reg_ex = /[9][9][0-9]{2}[a-zA-Z]{3}[0-9]{5}[O][S][0-9a-zA-Z]{1}/;
    // const tdsregx = /[0-9]{2}[a-zA-Z]{4}[a-zA-Z0-9]{1}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[D]{1}[0-9a-zA-Z]{1}/;
    // const tcsregx = /[0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[C]{1}[0-9a-zA-Z]{1}/;
    // const aridregx= /[0-9]{12}[A][R][0-9a-zA-Z]{1}/;
    // if (gstinregx.test(data) || uinregx.test(data) || nrid.test(data) || oidar_reg_ex.test(data) || tcsregx.test(data) ||tdsregx.test(data) ||aridregx.test(data)) {
    //   return true;
    // }
    const gstPattern = /[0-9]{2}[0-9A-Z]{13}/
    if(gstPattern.test(data)){
      return true;
    }
  }
  return false;
}
}

@NgModule({
  declarations: [
    ValidateGSTDirective 
  ],
  exports: [ValidateGSTDirective]
})
export class ValidateGSTDirectiveModule { }
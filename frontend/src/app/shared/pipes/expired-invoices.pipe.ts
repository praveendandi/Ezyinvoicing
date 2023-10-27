import { NgModule, Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'expiredInvoices'
})
export class ExpiredInvoicesPipe implements PipeTransform {

  transform(value: [], number?:any , gst?:any): any {
    if (!value) return null;   

    if (value && value.length) {
      return value.filter((item: any) => {
        if (number) {
            return item?.invoice_number?.toLowerCase()?.includes(number.toLowerCase());
        }
        if (gst ) {
            return item?.gst_number?.toLowerCase()?.includes(gst.toLowerCase());
        }      
        
        return true;
    })
    }else {
      return value;
  }

   
  }

}
@NgModule ({
  declarations: [ExpiredInvoicesPipe],
  exports : [ExpiredInvoicesPipe]
})
export class ExpiredInvoicesPipeModule {}

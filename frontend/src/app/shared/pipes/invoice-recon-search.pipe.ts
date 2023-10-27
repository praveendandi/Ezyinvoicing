import { NgModule, Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'invoiceReconSearch'
})
export class InvoiceReconSearchPipe implements PipeTransform {

  transform(value: [], date?:any ,): unknown {
    if (!value) return null;  

    if (value && value.length) {
      return value.filter((item: any) => {        

        if (date) {
            return item?.bill_generation_date?.toLowerCase()?.includes(date.toLowerCase());
        }
        
        return true;
    })
    }else {
      return value;
  }

  }

}
@NgModule ({
  declarations: [InvoiceReconSearchPipe],
  exports : [InvoiceReconSearchPipe]
})
export class InvoiceReconSearchPipeModule {}

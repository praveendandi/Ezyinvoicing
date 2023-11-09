import { NgModule, Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'filter'
})
export class FilterPipe implements PipeTransform {
    transform(value: any,type: string, input: any): any { 
        console.log("Value ===",value)
        console.log("Input ===",input,"type ===",type)
        if(!input)
        return value;
       return value.filter(
         item => {
          let valid = false;
           switch(type){
             case 'tradeName':
              item.trade_name.toString().toLowerCase().includes(input);
           }
           return valid;
         }
      );
        }

}

@NgModule({
  declarations: [FilterPipe],
  exports: [FilterPipe]
})
export class FilterPipeModule { }
import { NgModule, Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'noDataSign'
})
export class NoDataSignPipe implements PipeTransform {

  transform(value: unknown, ...args: unknown[]): unknown {
    if(value === "" || value == null){
      return '---'
    }else{
      return value
    }
  }

}
@NgModule ({
  declarations: [NoDataSignPipe],
  exports : [NoDataSignPipe]
})

export class NoDataSignPipeModule {}

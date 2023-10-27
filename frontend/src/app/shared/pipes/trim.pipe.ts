import { Pipe, PipeTransform, NgModule } from '@angular/core';

@Pipe({
  name: 'trim'
})
export class TrimPipe implements PipeTransform {

  transform(value: string): unknown {
    return (value || '').trim();
  }

}
@NgModule({
  declarations: [
    TrimPipe
  ],
  exports: [TrimPipe]

})
export class TrimPipeModule { }


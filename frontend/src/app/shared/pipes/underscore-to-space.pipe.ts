import { Pipe, PipeTransform, NgModule } from '@angular/core';

@Pipe({
  name: 'underscoreSpace'
})
export class UnderscoreToSpace implements PipeTransform {

  transform(value: string): unknown {
    return (value || '').replace(/_/g,' ');
  }

}
@NgModule({
  declarations: [
    UnderscoreToSpace
  ],
  exports: [UnderscoreToSpace]

})
export class UnderscoreToSpaceModule { }


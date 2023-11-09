import { NgModule, Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'searchFilter',
    pure: false
})
export class MyFilterPipe implements PipeTransform {

    transform(value: any, args?: any): any {
        if (!value) return null;
        if (!args) return value;

        args = args.toLowerCase();

        return value.filter(function (item) {
            return JSON.stringify(item).toLowerCase().includes(args);
        });
    }
}


@NgModule({
    declarations: [MyFilterPipe],
    exports: [MyFilterPipe]
  })
  export class MyFilterPipeModule { }
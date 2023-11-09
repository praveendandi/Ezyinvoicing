import { Directive, ElementRef, HostListener, NgModule } from '@angular/core';

@Directive({
  selector: '[appNumberInput]'
})
export class NumberInputDirective {

  constructor(private ele: ElementRef) { }

  @HostListener('input', ['$event']) onInputChange(event): void {
    const initalValue = this.ele.nativeElement.value;

    this.ele.nativeElement.value = initalValue.replace(/[^0-9]*/g, '');
    if (initalValue !== this.ele.nativeElement.value) {
      event.stopPropagation();
    }
  }
}

@NgModule({
  declarations: [NumberInputDirective],
  exports: [NumberInputDirective]
})

export class NumberInputDirectiveModule { }

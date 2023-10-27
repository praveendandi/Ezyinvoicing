import { Directive, ElementRef, HostListener, NgModule } from '@angular/core';

@Directive({
  selector: '[appAlphaInput]'
})
export class AlphaInputDirective {

  constructor(private ele: ElementRef) { }

  @HostListener('input', ['$event']) onInputChange(event:any): void {
    const initalValue = this.ele.nativeElement.value;

    this.ele.nativeElement.value = initalValue.replace(/[^a-zA-Z]*/g, '');
    if (initalValue !== this.ele.nativeElement.value) {
      event.stopPropagation();
    }
  }

}

@NgModule({
  declarations: [AlphaInputDirective],
  exports: [AlphaInputDirective]
})

export class AlphaInputDirectiveModule { }

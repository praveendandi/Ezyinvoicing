import { Directive, ElementRef, HostListener, NgModule } from '@angular/core';

@Directive({
  selector: '[noWhiteSpace]'
})
export class NoWhiteSpaceInputDirective {

    private regex: RegExp = new RegExp(/^([a-zA-Z1-9]{1}[a-zA-Z0-9\/-]{0,15})$/);
    private specialKeys: Array<string> = ['Backspace', 'Tab', 'End', 'Home', '-', 'ArrowLeft', 'ArrowRight', 'Del', 'Delete'];
    constructor(private el: ElementRef) {
    }
    @HostListener('keydown', ['$event'])
    onKeyDown(event: KeyboardEvent) {
      // console.log(this.el.nativeElement.value);
      // Allow Backspace, tab, end, and home keys
      if (this.specialKeys.indexOf(event.key) !== -1) {
        return;
      }
      let current: string = this.el.nativeElement.value;
      const position = this.el.nativeElement.selectionStart;
      const next: string = [current.slice(0, position), event.key, current.slice(position)].join('');
      if (next && !String(next).match(this.regex)) {
        event.preventDefault();
      }
    }

}

@NgModule({
  declarations: [NoWhiteSpaceInputDirective],
  exports: [NoWhiteSpaceInputDirective]
})

export class NoWhiteSpaceInputDirectiveModule { }

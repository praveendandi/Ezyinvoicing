import { Directive, ElementRef, HostListener, OnInit, DoCheck, NgModule } from '@angular/core';

@Directive({
  selector: '[appMatInput]',

})
export class MatInputDirective implements OnInit, DoCheck {
  inputElement: HTMLInputElement;
  constructor(public el: ElementRef) {
    this.inputElement = el.nativeElement;
  }

  ngDoCheck(): void {
    this.updateStyles();
  }

  ngOnInit(): void {
    this.updateStyles();
  }

  @HostListener('focus', ['$event'])
  onFocus(e): any {
    this.updateStyles();
  }

  @HostListener('focusout', ['$event'])
  onFocusOut(e): any {
    this.updateStyles();
  }

  /**
   * Updates styles
   */
  private updateStyles(): void {
    const label: HTMLLabelElement = this.inputElement.parentElement.querySelector('label');
    if (label) {
      label.classList.add('mat-label');
    }
    this.inputElement.classList.add('mat-input');
    if (this.inputElement.value) {
      if (label) {
        label.classList.add('mat-input-active');
      }
    } else {
      if (label) {
        if (this.inputElement == document.activeElement) {
          label.classList.add('mat-input-active');
        } else {
          label.classList.remove('mat-input-active');
        }
      }
    }
  }
}

@NgModule({
  declarations: [MatInputDirective],
  exports: [MatInputDirective]
})

export class MatInputDirectiveModule { }

import { Component } from '@angular/core';
import {
  animate,
  keyframes,
  state,
  style,
  transition,
  trigger
} from '@angular/animations';
import { Toast, ToastrService, ToastPackage, IndividualConfig} from 'ngx-toastr';

export interface IToastButton {
  id: string;
  title: string;
};

@Component({
  selector: 'app-custom-toastr',
  templateUrl: './custom-toastr.component.html',
  styleUrls: ['./custom-toastr.component.scss'],
  animations: [
    trigger('flyInOut', [
      state('inactive', style({
        opacity: 0,
      })),
      transition('inactive => active', animate('400ms ease-out', keyframes([
        style({
          transform: 'translate3d(100%, 0, 0) skewX(-30deg)',
          opacity: 0,
        }),
        style({
          transform: 'skewX(20deg)',
          opacity: 1,
        }),
        style({
          transform: 'skewX(-5deg)',
          opacity: 1,
        }),
        style({
          transform: 'none',
          opacity: 1,
        }),
      ]))),
      transition('active => removed', animate('400ms ease-out', keyframes([
        style({
          opacity: 1,
        }),
        style({
          transform: 'translate3d(100%, 0, 0) skewX(30deg)',
          opacity: 0,
        }),
      ]))),
    ]),
  ],
  preserveWhitespaces: false,
})
export class CustomToastrComponent extends Toast {

  // used for demo purposes
  undoString = 'undo';

  // constructor is only necessary when not using AoT
  constructor(
    protected toastrService: ToastrService,
    public toastPackage: ToastPackage,
  ) {
    super(toastrService, toastPackage);
  }

  action(btn) {
    console.log("+++",btn)
    event.stopPropagation();
    this.toastPackage.triggerAction(btn);
    this.toastrService.clear();
    return false;
  }

}

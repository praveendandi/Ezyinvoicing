import { DecimaNumberDirectiveModule } from './../../shared/directives/decimal-number.directive';
import { NumberInputDirectiveModule } from './../../shared/directives/number-input.directive';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ManualCreditNotesRoutingModule } from './manual-credit-notes-routing.module';
import { ManualCreditNotesComponent } from './manual-credit-notes.component';
import {MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { FormsModule } from '@angular/forms';
import { NgbTooltipModule } from '@ng-bootstrap/ng-bootstrap';
import { NgSelectModule } from '@ng-select/ng-select';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';
import { ValidateGSTDirectiveModule } from 'src/app/shared/directives/validate-gst.directive';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';
import { QuillModule } from 'ngx-quill';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';


@NgModule({
  declarations: [ManualCreditNotesComponent],
  imports: [
    CommonModule,
    ManualCreditNotesRoutingModule,
    MatInputDirectiveModule,
    FormsModule,
    NgbTooltipModule,
    NgSelectModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
    NumberInputDirectiveModule,
    DecimaNumberDirectiveModule,
    ValidateGSTDirectiveModule,
    VirtualScrollerModule,
    PermissionButtonDirectiveModule,
    QuillModule.forRoot()
  ]
})
export class ManualCreditNotesModule { }

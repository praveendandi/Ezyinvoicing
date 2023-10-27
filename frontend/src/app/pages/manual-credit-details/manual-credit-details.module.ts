import { NumberInputDirectiveModule } from './../../shared/directives/number-input.directive';
import { DecimaNumberDirectiveModule } from './../../shared/directives/decimal-number.directive';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ManualCreditDetailsRoutingModule } from './manual-credit-details-routing.module';
import { ManualCreditDetailsComponent } from './manual-credit-details.component';
import { NgbActiveModal, NgbNavModule, NgbTooltipModule,NgbDropdownModule, NgbTypeaheadModule } from '@ng-bootstrap/ng-bootstrap';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { FormsModule } from '@angular/forms';
import { NgSelectModule } from '@ng-select/ng-select';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';
import { ValidateGSTDirectiveModule } from 'src/app/shared/directives/validate-gst.directive';
import { SafePipeModule } from 'src/app/shared/pipes/safe.pipe';
import { QuillModule } from 'ngx-quill';
import { TrimPipeModule } from './../../shared/pipes/trim.pipe';
import { AmountToWordPipeModule } from 'src/app/shared/pipes/amount-to-word.pipe';
import { NgxJsonViewerModule } from 'ngx-json-viewer';


@NgModule({
  declarations: [ManualCreditDetailsComponent],
  imports: [
    CommonModule,
    ManualCreditDetailsRoutingModule,
    NgbNavModule,
    MatInputDirectiveModule,
    FormsModule,
    NgSelectModule,
    OwlDateTimeModule,
    NgbTooltipModule,
    OwlNativeDateTimeModule,
    DecimaNumberDirectiveModule,
    NumberInputDirectiveModule,
    ValidateGSTDirectiveModule,
    NgbDropdownModule,
    SafePipeModule,
    QuillModule.forRoot(),
    TrimPipeModule,
    AmountToWordPipeModule,
    NgxJsonViewerModule
  ],
})
export class ManualCreditDetailsModule { }

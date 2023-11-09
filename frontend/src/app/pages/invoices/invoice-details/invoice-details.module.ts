import { OwlDateTimeModule, OwlNativeDateTimeModule, OWL_DATE_TIME_LOCALE } from 'ng-pick-datetime';
import { FormsModule } from '@angular/forms';
import { TrimPipeModule } from './../../../shared/pipes/trim.pipe';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { InvoiceDetailsRoutingModule } from './invoice-details-routing.module';
import { InvoiceDetailsComponent } from './invoice-details.component';
import { NgbDropdownModule, NgbNavModule, NgbTooltipModule } from '@ng-bootstrap/ng-bootstrap';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { UnderscoreToSpaceModule } from 'src/app/shared/pipes/underscore-to-space.pipe';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';
import { SafePipeModule } from 'src/app/shared/pipes/safe.pipe';
import { QuillModule } from 'ngx-quill';
import { SacHsnModule } from 'src/app/shared/models/sac-hsn/sac-hsn.module';
import { TempSacLineModule } from 'src/app/shared/models/temp-sac-line/temp-sac-line.module';
import { ValidateGSTDirectiveModule } from 'src/app/shared/directives/validate-gst.directive';
import { NgSelectModule } from '@ng-select/ng-select';
import { NgxJsonViewerModule } from 'ngx-json-viewer';
import { AmountToWordPipeModule } from '../../../shared/pipes/amount-to-word.pipe';

@NgModule({
  declarations: [InvoiceDetailsComponent],
  imports: [
    CommonModule,
    FormsModule,
    InvoiceDetailsRoutingModule,
    NgbNavModule,
    MatInputDirectiveModule,
    TrimPipeModule,
    NgbTooltipModule,
    UnderscoreToSpaceModule,
    PermissionButtonDirectiveModule,
    SafePipeModule,
    NgbDropdownModule,
    QuillModule.forRoot(),
    SacHsnModule,
    TempSacLineModule,
    ValidateGSTDirectiveModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
    NgSelectModule,
    NgxJsonViewerModule,
    AmountToWordPipeModule
  ],
  providers:[
    { provide: OWL_DATE_TIME_LOCALE, useValue: 'en-GB' }
  ]
})
export class InvoiceDetailsModule { }

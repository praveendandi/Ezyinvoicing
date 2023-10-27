import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { UploadInvoicesRoutingModule } from './upload-invoices-routing.module';
import { UploadInvoicesComponent } from './upload-invoices.component';
import { FormsModule } from '@angular/forms';
import { SafePipeModule } from 'src/app/shared/pipes/safe.pipe';
import { NgbNavModule, NgbTooltipModule } from '@ng-bootstrap/ng-bootstrap';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';


@NgModule({
  declarations: [UploadInvoicesComponent],
  imports: [
    CommonModule,
    FormsModule,
    UploadInvoicesRoutingModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
    NgbTooltipModule,
    MatInputDirectiveModule,
    PermissionButtonDirectiveModule,
    NgbNavModule,
    SafePipeModule
  ]
})
export class UploadInvoicesModule { }

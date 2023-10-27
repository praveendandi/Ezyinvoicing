import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TaxPayersDetailsComponent } from './tax-payers-details.component';
import { FormsModule } from '@angular/forms';
import { TaxPayersDetailsRoutingModule } from './tax-payers-details-routing.module';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';
import { ValidateGSTDirectiveModule } from 'src/app/shared/directives/validate-gst.directive';



@NgModule({
  declarations: [TaxPayersDetailsComponent],
  imports: [
    CommonModule,
    TaxPayersDetailsRoutingModule,
    FormsModule,
    MatInputDirectiveModule,
    PermissionButtonDirectiveModule,
    ValidateGSTDirectiveModule
  ]
})
export class TaxPayersDetailsModule { }

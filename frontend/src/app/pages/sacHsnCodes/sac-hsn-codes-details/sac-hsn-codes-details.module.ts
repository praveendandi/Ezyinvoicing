import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SacHsnCodesDetailsRoutingModule } from './sac-hsn-codes-details-routing.module';
import { SacHsnCodesDetailsComponent } from './sac-hsn-codes-details.component';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { FormsModule } from '@angular/forms';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';


@NgModule({
  declarations: [SacHsnCodesDetailsComponent],
  imports: [
    CommonModule,
    SacHsnCodesDetailsRoutingModule,
    MatInputDirectiveModule,
    FormsModule,
    PermissionButtonDirectiveModule
  ]
})
export class SacHsnCodesDetailsModule { }

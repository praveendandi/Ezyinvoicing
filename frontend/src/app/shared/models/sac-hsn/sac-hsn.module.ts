import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SacHsnRoutingModule } from './sac-hsn-routing.module';
import { SacHsnComponent } from './sac-hsn.component';
import { FormsModule } from '@angular/forms';
import { PermissionButtonDirectiveModule } from '../../directives/permission-button.directive';
import { MatInputDirectiveModule } from '../../directives/mat-input.directive';
import { NumberInputDirectiveModule } from '../../directives/number-input.directive';
import { DecimaNumberDirectiveModule } from '../../directives/decimal-number.directive';


@NgModule({
  declarations: [SacHsnComponent],
  imports: [
    CommonModule,
    SacHsnRoutingModule,
    FormsModule,
    PermissionButtonDirectiveModule,
    MatInputDirectiveModule,
    NumberInputDirectiveModule,
    DecimaNumberDirectiveModule
  ],
  exports:[SacHsnComponent],
})
export class SacHsnModule { }

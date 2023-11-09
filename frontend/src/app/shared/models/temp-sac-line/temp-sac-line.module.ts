import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { TempSacLineRoutingModule } from './temp-sac-line-routing.module';
import { TempSacLineComponent } from './temp-sac-line.component';
import { FormsModule } from '@angular/forms';
import { DecimaNumberDirectiveModule } from '../../directives/decimal-number.directive';
import { NumberInputDirectiveModule } from '../../directives/number-input.directive';
import { MatInputDirectiveModule } from '../../directives/mat-input.directive';
import { PermissionButtonDirectiveModule } from '../../directives/permission-button.directive';


@NgModule({
  declarations: [TempSacLineComponent],
  imports: [
    CommonModule,
    TempSacLineRoutingModule,
    FormsModule,
    PermissionButtonDirectiveModule,
    MatInputDirectiveModule,
    NumberInputDirectiveModule,
    DecimaNumberDirectiveModule
  ],
  exports:[TempSacLineComponent]
})
export class TempSacLineModule { }

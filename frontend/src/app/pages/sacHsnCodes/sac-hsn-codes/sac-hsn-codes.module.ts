import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SacHsnCodesRoutingModule } from './sac-hsn-codes-routing.module';
import { SacHsnCodesComponent } from './sac-hsn-codes.component';
import { NgxPaginationModule } from 'ngx-pagination';
import { FormsModule } from '@angular/forms';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { NumberInputDirectiveModule } from 'src/app/shared/directives/number-input.directive';
import { DecimaNumberDirectiveModule } from 'src/app/shared/directives/decimal-number.directive';
import { SacHsnModule } from 'src/app/shared/models/sac-hsn/sac-hsn.module';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';


@NgModule({
  declarations: [SacHsnCodesComponent],
  imports: [
    CommonModule,
    FormsModule,
    SacHsnCodesRoutingModule,
    NgxPaginationModule,
    PermissionButtonDirectiveModule,
    MatInputDirectiveModule,
    NumberInputDirectiveModule,
    DecimaNumberDirectiveModule,
    SacHsnModule,
    VirtualScrollerModule
  ]
})
export class SacHsnCodesModule { }

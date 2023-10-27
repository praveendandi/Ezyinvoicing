import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AdjustmentOfAdvancesRoutingModule } from './adjustment-of-advances-routing.module';
import { AdjustmentOfAdvancesComponent } from './adjustment-of-advances.component';
import { SharedModule } from 'src/app/shared/shared.module';


@NgModule({
  declarations: [
    AdjustmentOfAdvancesComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    AdjustmentOfAdvancesRoutingModule
  ]
})
export class AdjustmentOfAdvancesModule { }

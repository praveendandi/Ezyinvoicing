import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AdvanceReceivedRoutingModule } from './advance-received-routing.module';
import { AdvanceReceivedComponent } from './advance-received.component';
import { SharedModule } from 'src/app/shared/shared.module';


@NgModule({
  declarations: [
    AdvanceReceivedComponent
  ],
  imports: [
    CommonModule,
    AdvanceReceivedRoutingModule,
    SharedModule
  ]
})
export class AdvanceReceivedModule { }

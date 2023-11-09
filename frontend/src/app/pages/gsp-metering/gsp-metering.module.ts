import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { GspMeteringRoutingModule } from './gsp-metering-routing.module';
import { GspMeteringComponent } from './gsp-metering.component';
import { FormsModule } from '@angular/forms';


@NgModule({
  declarations: [GspMeteringComponent],
  imports: [
    CommonModule,
    GspMeteringRoutingModule,
    FormsModule
  ]
})
export class GspMeteringModule { }

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ReconciliationRoutingModule } from './reconciliation-routing.module';
import { ReconciliationComponent } from './reconciliation.component';
import { FormsModule } from '@angular/forms';


@NgModule({
  declarations: [
    ReconciliationComponent
  ],
  imports: [
    CommonModule,
    ReconciliationRoutingModule,
    FormsModule
  ]
})
export class ReconciliationModule { }

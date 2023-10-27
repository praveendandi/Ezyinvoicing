import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Gstr2ReconciliationRoutingModule } from './gstr2-reconciliation-routing.module';
import { Gstr2ReconciliationComponent } from './gstr2-reconciliation.component';
import { FormsModule } from '@angular/forms';


@NgModule({
  declarations: [
    Gstr2ReconciliationComponent
  ],
  imports: [
    CommonModule,
    Gstr2ReconciliationRoutingModule,
    FormsModule
  ]
})
export class Gstr2ReconciliationModule { }

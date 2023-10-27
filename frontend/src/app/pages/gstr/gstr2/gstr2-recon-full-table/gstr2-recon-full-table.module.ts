import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Gstr2ReconFullTableRoutingModule } from './gstr2-recon-full-table-routing.module';
import { Gstr2ReconFullTableComponent } from './gstr2-recon-full-table.component';


@NgModule({
  declarations: [
    Gstr2ReconFullTableComponent
  ],
  imports: [
    CommonModule,
    Gstr2ReconFullTableRoutingModule
  ]
})
export class Gstr2ReconFullTableModule { }

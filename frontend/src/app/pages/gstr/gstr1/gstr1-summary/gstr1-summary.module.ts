import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Gstr1SummaryRoutingModule } from './gstr1-summary-routing.module';
import { Gstr1SummaryComponent } from './gstr1-summary.component';
import { NgbTooltipModule } from '@ng-bootstrap/ng-bootstrap';


@NgModule({
  declarations: [
    Gstr1SummaryComponent
  ],
  imports: [
    CommonModule,
    Gstr1SummaryRoutingModule,
    NgbTooltipModule
  ]
})
export class Gstr1SummaryModule { }

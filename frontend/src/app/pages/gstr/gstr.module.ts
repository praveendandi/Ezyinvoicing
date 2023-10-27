import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { GstrRoutingModule } from './gstr-routing.module';
import { GstrComponent } from './gstr.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { FormsModule } from '@angular/forms';
import { NoDataSignPipeModule } from 'src/app/shared/pipes/no-data-sign.pipe';
import { GoogleChartsModule } from 'angular-google-charts';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { SharedModule } from 'src/app/shared/shared.module';


@NgModule({
  declarations: [
    GstrComponent,
    DashboardComponent,
  ],
  imports: [
    CommonModule,
    GstrRoutingModule,
    NoDataSignPipeModule,
    GoogleChartsModule,
    FormsModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
    NgbModule,
    SharedModule
  ]
})
export class GstrModule { }

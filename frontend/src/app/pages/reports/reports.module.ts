import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ReportsRoutingModule } from './reports-routing.module';
import { ReportsComponent } from './reports.component';
import { NgbDropdownModule } from '@ng-bootstrap/ng-bootstrap';
import { FormsModule } from '@angular/forms';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';


@NgModule({
  declarations: [ReportsComponent],
  imports: [
    CommonModule,
    ReportsRoutingModule,
    NgbDropdownModule,
    FormsModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
    PermissionButtonDirectiveModule
  ]
})
export class ReportsModule { }

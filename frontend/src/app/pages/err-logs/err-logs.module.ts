import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ErrLogsRoutingModule } from './err-logs-routing.module';
import { ErrLogsComponent } from './err-logs.component';
import { FormsModule } from '@angular/forms';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';


@NgModule({
  declarations: [ErrLogsComponent],
  imports: [
    CommonModule,
    ErrLogsRoutingModule,
    FormsModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule
  ]
})
export class ErrLogsModule { }

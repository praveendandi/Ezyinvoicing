import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { BenchLogsRoutingModule } from './bench-logs-routing.module';
import { BenchLogsComponent } from './bench-logs.component';


@NgModule({
  declarations: [BenchLogsComponent],
  imports: [
    CommonModule,
    BenchLogsRoutingModule
  ],
  exports: []
})
export class BenchLogsModule { }

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { BenchLogDetailsRoutingModule } from './bench-log-details-routing.module';
import { BenchLogDetailsComponent } from './bench-log-details.component';
import { FormsModule } from '@angular/forms';


@NgModule({
  declarations: [BenchLogDetailsComponent],
  imports: [
    CommonModule,
    BenchLogDetailsRoutingModule,
    FormsModule
  ]
})
export class BenchLogDetailsModule { }

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { IpPrintersRoutingModule } from './ip-printers-routing.module';
import { IpPrintersComponent } from './ip-printers.component';
import { FormsModule } from '@angular/forms';


@NgModule({
  declarations: [IpPrintersComponent],
  imports: [
    CommonModule,
    IpPrintersRoutingModule,
    FormsModule
  ]
})
export class IpPrintersModule { }

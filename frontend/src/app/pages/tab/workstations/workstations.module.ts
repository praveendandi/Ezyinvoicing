import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { WorkstationsRoutingModule } from './workstations-routing.module';
import { WorkstationsComponent } from './workstations.component';
import { FormsModule } from '@angular/forms';
import { NgxQRCodeModule } from '@techiediaries/ngx-qrcode';


@NgModule({
  declarations: [WorkstationsComponent],
  imports: [
    CommonModule,
    WorkstationsRoutingModule,
    FormsModule,
    NgxQRCodeModule
  ]
})
export class WorkstationsModule { }

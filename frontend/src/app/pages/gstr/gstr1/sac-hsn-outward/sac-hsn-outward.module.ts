import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SacHsnOutwardRoutingModule } from './sac-hsn-outward-routing.module';
import { SacHsnOutwardComponent } from './sac-hsn-outward.component';
import { FormsModule } from '@angular/forms';
import { NgbDropdownModule } from '@ng-bootstrap/ng-bootstrap';
import { SharedModule } from 'src/app/shared/shared.module';
import { NgSelectModule } from '@ng-select/ng-select';


@NgModule({
  declarations: [
    SacHsnOutwardComponent
  ],
  imports: [
    CommonModule,
    SacHsnOutwardRoutingModule,
    FormsModule,
    NgbDropdownModule,
    SharedModule,
    NgSelectModule
  ]
})
export class SacHsnOutwardModule { }

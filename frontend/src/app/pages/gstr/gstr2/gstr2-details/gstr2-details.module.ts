import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Gstr2DetailsRoutingModule } from './gstr2-details-routing.module';
import { Gstr2DetailsComponent } from './gstr2-details.component';
import { NgbDropdownModule } from '@ng-bootstrap/ng-bootstrap';
import { FormsModule } from '@angular/forms';


@NgModule({
  declarations: [
    Gstr2DetailsComponent
  ],
  imports: [
    CommonModule,
    Gstr2DetailsRoutingModule,
    NgbDropdownModule,
    FormsModule
  ]
})
export class Gstr2DetailsModule { }

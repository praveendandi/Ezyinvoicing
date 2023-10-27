import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Gstr2RoutingModule } from './gstr2-routing.module';
import { Gstr2Component } from './gstr2.component';
import { FormsModule } from '@angular/forms';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { SharedModule } from 'src/app/shared/shared.module';

@NgModule({
  declarations: [Gstr2Component],
  imports: [
    CommonModule,
    Gstr2RoutingModule,
    FormsModule,
    NgbModule,
    SharedModule
  ]
})
export class Gstr2Module { }

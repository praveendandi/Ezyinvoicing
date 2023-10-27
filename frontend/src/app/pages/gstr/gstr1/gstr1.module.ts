import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Gstr1RoutingModule } from './gstr1-routing.module';
import { Gstr1Component } from './gstr1.component';
import { FormsModule } from '@angular/forms';
import { SharedModule } from 'src/app/shared/shared.module';
import { NgSelectModule } from '@ng-select/ng-select';


@NgModule({
  declarations: [
    Gstr1Component
  ],
  imports: [
    CommonModule,
    Gstr1RoutingModule,
    FormsModule,
    SharedModule,
    NgSelectModule
  ]
})
export class Gstr1Module { }

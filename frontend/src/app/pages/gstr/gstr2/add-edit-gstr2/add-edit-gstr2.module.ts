import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AddEditGstr2RoutingModule } from './add-edit-gstr2-routing.module';
import { AddEditGstr2Component } from './add-edit-gstr2.component';
import { FormsModule } from '@angular/forms';


@NgModule({
  declarations: [
    AddEditGstr2Component
  ],
  imports: [
    CommonModule,
    AddEditGstr2RoutingModule,
    FormsModule
  ]
})
export class AddEditGstr2Module { }

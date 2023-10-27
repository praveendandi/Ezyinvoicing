import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SaveGstinRoutingModule } from './save-gstin-routing.module';
import { SaveGstinComponent } from './save-gstin.component';
import { FormsModule } from '@angular/forms';


@NgModule({
  declarations: [
    SaveGstinComponent
  ],
  imports: [
    CommonModule,
    SaveGstinRoutingModule,
    FormsModule
  ]
})
export class SaveGstinModule { }

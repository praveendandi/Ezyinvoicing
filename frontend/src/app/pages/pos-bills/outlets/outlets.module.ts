import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { OutletsRoutingModule } from './outlets-routing.module';
import { OutletsComponent } from './outlets.component';
import { FormsModule } from '@angular/forms';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { ValidateGSTDirectiveModule } from 'src/app/shared/directives/validate-gst.directive';


@NgModule({
  declarations: [OutletsComponent],
  imports: [
    CommonModule,
    OutletsRoutingModule,
    FormsModule,
    MatInputDirectiveModule,
    ValidateGSTDirectiveModule
  ]
})
export class OutletsModule { }

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { NillRatedRoutingModule } from './nill-rated-routing.module';
import { NillRatedComponent } from './nill-rated.component';
import { SharedModule } from 'src/app/shared/shared.module';
import { FormsModule } from '@angular/forms';
import { NgbNavModule } from '@ng-bootstrap/ng-bootstrap';


@NgModule({
  declarations: [
    NillRatedComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    NgbNavModule,
    FormsModule,
    NillRatedRoutingModule
  ]
})
export class NillRatedModule { }

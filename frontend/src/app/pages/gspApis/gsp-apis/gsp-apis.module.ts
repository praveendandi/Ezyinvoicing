import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { GspApisRoutingModule } from './gsp-apis-routing.module';
import { GspApisComponent } from './gsp-apis.component';
import { NgxPaginationModule } from 'ngx-pagination';


@NgModule({
  declarations: [GspApisComponent],
  imports: [
    CommonModule,
    GspApisRoutingModule,
    NgxPaginationModule
  ]
})
export class GspApisModule { }

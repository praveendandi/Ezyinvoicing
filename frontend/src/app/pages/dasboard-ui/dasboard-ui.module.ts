import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DasboardUiRoutingModule } from './dasboard-ui-routing.module';
import { DasboardUiComponent } from './dasboard-ui.component';
import { NgbPagination, NgbPaginationModule, NgbProgressbarModule } from '@ng-bootstrap/ng-bootstrap';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';


@NgModule({
  declarations: [DasboardUiComponent],
  imports: [
    CommonModule,
    DasboardUiRoutingModule,
    NgbProgressbarModule,
    HttpClientModule,
    FormsModule,
    NgbPaginationModule,
    NgxSkeletonLoaderModule.forRoot({ animation: 'pulse' })
  ]
})
export class DasboardUiModule { }

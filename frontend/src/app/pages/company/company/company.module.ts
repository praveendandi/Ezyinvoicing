import { FormsModule } from '@angular/forms';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { CompanyRoutingModule } from './company-routing.module';
import { CompanyComponent } from './company.component';
import { CompanyService } from '../company.service';
import { NgxPaginationModule } from 'ngx-pagination';


@NgModule({
  declarations: [CompanyComponent],
  imports: [
    CommonModule,
    FormsModule,
    CompanyRoutingModule,
    NgxPaginationModule
  ],
  providers: [CompanyService]
})
export class CompanyModule { }

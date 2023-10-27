import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { CompanyDetailsRoutingModule } from './company-details-routing.module';
import { CompanyDetailsComponent } from './company-details.component';
import { CompanyService } from '../company.service';
import { FormsModule } from '@angular/forms';
import { NumberInputDirectiveModule } from 'src/app/shared/directives/number-input.directive';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { NgbAccordionModule, NgbTypeaheadModule } from '@ng-bootstrap/ng-bootstrap';
import { QuillModule } from 'ngx-quill';
import { NgbNavModule } from '@ng-bootstrap/ng-bootstrap';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';


@NgModule({
  declarations: [CompanyDetailsComponent],
  imports: [
    CommonModule,
    CompanyDetailsRoutingModule,
    FormsModule,
    NumberInputDirectiveModule,
    NgbTypeaheadModule,
    MatInputDirectiveModule,
    NgbAccordionModule,
    QuillModule,
    NgbNavModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
  ],
  providers: [CompanyService]
})
export class CompanyDetailsModule { }

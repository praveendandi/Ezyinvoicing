import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { GspApisDetailsRoutingModule } from './gsp-apis-details-routing.module';
import { GspApisDetailsComponent } from './gsp-apis-details.component';
import { FormsModule } from '@angular/forms';
import { NumberInputDirectiveModule } from 'src/app/shared/directives/number-input.directive';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { NgbAccordionModule } from '@ng-bootstrap/ng-bootstrap';


@NgModule({
  declarations: [GspApisDetailsComponent],
  imports: [
    CommonModule,
    GspApisDetailsRoutingModule,
    FormsModule,
    NumberInputDirectiveModule,
    MatInputDirectiveModule,
    NgbAccordionModule
  ]
})
export class GspApisDetailsModule { }

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { EmailSettingsRoutingModule } from './email-settings-routing.module';
import { EmailSettingsComponent } from './email-settings.component';
import { FormsModule } from '@angular/forms';
import { NgbAccordionModule, NgbTypeaheadModule } from '@ng-bootstrap/ng-bootstrap';
import { NumberInputDirectiveModule } from 'src/app/shared/directives/number-input.directive';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { QuillModule } from 'ngx-quill';


@NgModule({
  declarations: [EmailSettingsComponent],
  imports: [
    CommonModule,
    FormsModule,
    EmailSettingsRoutingModule,
    NumberInputDirectiveModule,
    NgbTypeaheadModule,
    MatInputDirectiveModule,
    NgbAccordionModule,
    QuillModule.forRoot()
  ]
})
export class EmailSettingsModule { }

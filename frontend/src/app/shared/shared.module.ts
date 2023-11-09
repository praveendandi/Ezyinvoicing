
import { NgModule } from '@angular/core';
import { CommonModule } from "@angular/common";
import { RetPeriodComponent } from '../resuable/ret-period/ret-period.component';
import { FormsModule } from '@angular/forms';
import { SearchByInputComponent } from '../resuable/search-by-input/search-by-input.component';
import { NgbDropdownModule } from '@ng-bootstrap/ng-bootstrap';
import { UploadExcelFileComponent } from './models/upload-excel-file/upload-excel-file.component';

@NgModule({
  exports: [
    CommonModule,
    RetPeriodComponent,
    SearchByInputComponent
  ],

  imports: [
    CommonModule,
    FormsModule,
    NgbDropdownModule
  ],
  declarations: [
    RetPeriodComponent,
    SearchByInputComponent,
    UploadExcelFileComponent
  ],

})

export class SharedModule { }

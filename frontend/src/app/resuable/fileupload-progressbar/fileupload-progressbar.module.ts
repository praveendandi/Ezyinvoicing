import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FileuploadProgressbarComponent } from './fileupload-progressbar.component';
import { FileuploadProgressbarService } from './fileupload-progressbar.service';
import { NgbAccordionModule } from '@ng-bootstrap/ng-bootstrap';



@NgModule({
  declarations: [],
  imports: [
    CommonModule,
  ],
  providers:[FileuploadProgressbarService]
})
export class FileuploadProgressbarModule { }

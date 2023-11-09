import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DeletedDocumentsRoutingModule } from './deleted-documents-routing.module';
import { DeletedDocumentsComponent } from './deleted-documents.component';
import { FormsModule } from '@angular/forms';
import { NgbModalModule } from '@ng-bootstrap/ng-bootstrap';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';


@NgModule({
  declarations: [DeletedDocumentsComponent],
  imports: [
    CommonModule,
    DeletedDocumentsRoutingModule,
    FormsModule,
    NgbModalModule,
    VirtualScrollerModule
  ]
})
export class DeletedDocumentsModule { }

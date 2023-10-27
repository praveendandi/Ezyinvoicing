import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DocumentBinRoutingModule } from './document-bin-routing.module';
import { DocumentBinComponent } from './document-bin.component';
import { FormsModule } from '@angular/forms';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';
import { NgbTooltipModule } from '@ng-bootstrap/ng-bootstrap';
import { ClipboardModule } from 'ngx-clipboard';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';

@NgModule({
  declarations: [DocumentBinComponent],
  imports: [
    CommonModule,
    DocumentBinRoutingModule,
    FormsModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
    NgbTooltipModule,
    ClipboardModule,
    VirtualScrollerModule,
    PermissionButtonDirectiveModule
  ]
})
export class DocumentBinModule { }

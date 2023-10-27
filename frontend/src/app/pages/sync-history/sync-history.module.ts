import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SyncHistoryRoutingModule } from './sync-history-routing.module';
import { SyncHistoryComponent } from './sync-history.component';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';
import { FormsModule } from '@angular/forms';
import { NgSelectModule } from '@ng-select/ng-select';
import { SafePipeModule } from 'src/app/shared/pipes/safe.pipe';
import { NgbDropdownModule, NgbNavModule, NgbProgressbarModule, NgbTooltipModule } from '@ng-bootstrap/ng-bootstrap';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';
import { Ng2SearchPipeModule } from 'ng2-search-filter';


@NgModule({
  declarations: [SyncHistoryComponent],
  imports: [
    CommonModule,
    FormsModule,
    SyncHistoryRoutingModule,
    VirtualScrollerModule,
    CommonModule,
    FormsModule,
    NgSelectModule,
    SafePipeModule,
    NgbTooltipModule,
    MatInputDirectiveModule,
    OwlDateTimeModule,
    VirtualScrollerModule,
    OwlNativeDateTimeModule,
    NgbNavModule,
    NgbDropdownModule,
    NgbProgressbarModule,
    Ng2SearchPipeModule
  ]
})
export class SyncHistoryModule { }

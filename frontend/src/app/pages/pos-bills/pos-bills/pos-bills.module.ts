import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { PosBillsRoutingModule } from './pos-bills-routing.module';
import { PosBillsComponent } from './pos-bills.component';
import { FormsModule } from '@angular/forms';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';
import { NgbNavModule, NgbProgressbarModule } from '@ng-bootstrap/ng-bootstrap';
import { NgSelectModule } from '@ng-select/ng-select';
import { SafePipeModule } from 'src/app/shared/pipes/safe.pipe';
import { NgbDropdownModule, NgbTooltipModule } from '@ng-bootstrap/ng-bootstrap';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';

@NgModule({
  declarations: [PosBillsComponent],
  imports: [
    CommonModule,
    PosBillsRoutingModule,
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
    PermissionButtonDirectiveModule
  ]
})
export class PosBillsModule { }

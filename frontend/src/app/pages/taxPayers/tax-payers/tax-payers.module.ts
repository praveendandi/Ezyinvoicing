import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TaxPayersComponent } from './tax-payers.component';
import { TaxPayersRoutingModule } from './tax-payer-routing.module';
import { NgxPaginationModule } from 'ngx-pagination';
import { FormsModule } from '@angular/forms';
import { FilterPipeModule } from 'src/app/shared/pipes/sac-search.pipe';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';



@NgModule({
  declarations: [TaxPayersComponent],
  imports: [
    CommonModule,
    TaxPayersRoutingModule,
    NgxPaginationModule,
    FormsModule,
    FilterPipeModule,
    PermissionButtonDirectiveModule
  ]
})
export class TaxPayersModule { }

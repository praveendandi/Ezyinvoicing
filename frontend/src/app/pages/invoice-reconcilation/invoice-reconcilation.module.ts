import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { InvoiceReconcilationRoutingModule } from './invoice-reconcilation-routing.module';
import { InvoiceReconcilationComponent } from './invoice-reconcilation.component';
import { FormsModule } from '@angular/forms';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { NgSelectModule } from '@ng-select/ng-select';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';
import { NgxPaginationModule } from 'ngx-pagination';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';
import { InvoiceReconSearchPipeModule } from 'src/app/shared/pipes/invoice-recon-search.pipe';
import { NgbProgressbarModule } from '@ng-bootstrap/ng-bootstrap';


@NgModule({
  declarations: [InvoiceReconcilationComponent],
  imports: [
    CommonModule,
    InvoiceReconcilationRoutingModule,
    FormsModule,
    NgxPaginationModule,
    PermissionButtonDirectiveModule,
    NgSelectModule,
    MatInputDirectiveModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
    InvoiceReconSearchPipeModule,
    NgbProgressbarModule
  ]
})
export class InvoiceReconcilationModule { }

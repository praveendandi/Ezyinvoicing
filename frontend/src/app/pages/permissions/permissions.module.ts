import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { PermissionsRoutingModule } from './permissions-routing.module';
import { PermissionsComponent } from './permissions.component';
import { FormsModule } from '@angular/forms';
import { NgxPaginationModule } from 'ngx-pagination';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { SearchPermissionPipeModule } from 'src/app/shared/pipes/search-user.pipe';


@NgModule({
  declarations: [PermissionsComponent],
  imports: [
    CommonModule,
    PermissionsRoutingModule,
    FormsModule,
    NgxPaginationModule,
    MatInputDirectiveModule,
    SearchPermissionPipeModule
  ]
})
export class PermissionsModule { }

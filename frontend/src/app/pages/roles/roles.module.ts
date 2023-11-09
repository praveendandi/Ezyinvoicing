import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { RolesRoutingModule } from './roles-routing.module';
import { RolesComponent } from './roles.component';
import { FormsModule } from '@angular/forms';
import { NgxPaginationModule } from 'ngx-pagination';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';


@NgModule({
  declarations: [RolesComponent],
  imports: [
    CommonModule,
    RolesRoutingModule,
    FormsModule,
    NgxPaginationModule,
    PermissionButtonDirectiveModule
  ]
})
export class RolesModule { }

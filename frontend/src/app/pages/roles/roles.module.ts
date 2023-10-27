import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { RolesRoutingModule } from './roles-routing.module';
import { RolesComponent } from './roles.component';
import { FormsModule } from '@angular/forms';
import { NgxPaginationModule } from 'ngx-pagination';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';
import { AlphaInputDirectiveModule } from 'src/app/shared/directives/alpha-input.directive';


@NgModule({
  declarations: [RolesComponent],
  imports: [
    CommonModule,
    RolesRoutingModule,
    FormsModule,
    NgxPaginationModule,
    PermissionButtonDirectiveModule,
    AlphaInputDirectiveModule
  ]
})
export class RolesModule { }

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { UserDetailsRoutingModule } from './user-details-routing.module';
import { UserDetailsComponent } from './user-details.component';
import { FormsModule } from '@angular/forms';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { NgSelectModule } from '@ng-select/ng-select';


@NgModule({
  declarations: [UserDetailsComponent],
  imports: [
    CommonModule,
    UserDetailsRoutingModule,
    FormsModule,
    PermissionButtonDirectiveModule,
    MatInputDirectiveModule,
    NgSelectModule
  ]
})
export class UserDetailsModule { }

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UsersRoutingModule } from './users-routing.module';
import { UsersComponent } from './users.component';
import { FormsModule } from '@angular/forms';
import { NgxPaginationModule } from 'ngx-pagination';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';
import { NgSelectModule } from '@ng-select/ng-select';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { NgbNavModule } from '@ng-bootstrap/ng-bootstrap';

@NgModule({
  declarations: [UsersComponent],
  imports: [
    CommonModule,
    FormsModule,
    UsersRoutingModule,
    NgxPaginationModule,
    PermissionButtonDirectiveModule,
    NgSelectModule,
    MatInputDirectiveModule,
    NgbNavModule
  ]
})
export class UsersModule { }

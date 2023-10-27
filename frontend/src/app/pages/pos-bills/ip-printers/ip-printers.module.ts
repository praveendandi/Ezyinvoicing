import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { IpPrintersRoutingModule } from './ip-printers-routing.module';
import { IpPrintersComponent } from './ip-printers.component';
import { FormsModule } from '@angular/forms';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';


@NgModule({
  declarations: [IpPrintersComponent],
  imports: [
    CommonModule,
    IpPrintersRoutingModule,
    FormsModule,
    PermissionButtonDirectiveModule
  ]
})
export class IpPrintersModule { }

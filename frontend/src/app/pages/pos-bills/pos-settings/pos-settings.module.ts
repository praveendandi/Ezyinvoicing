import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { PosSettingsRoutingModule } from './pos-settings-routing.module';
import { PosSettingsComponent } from './pos-settings.component';
import { FormsModule } from '@angular/forms';


@NgModule({
  declarations: [PosSettingsComponent],
  imports: [
    CommonModule,
    PosSettingsRoutingModule,
    FormsModule
  ]
})
export class PosSettingsModule { }

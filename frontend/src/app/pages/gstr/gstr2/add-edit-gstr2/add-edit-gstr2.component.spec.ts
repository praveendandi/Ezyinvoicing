import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddEditGstr2Component } from './add-edit-gstr2.component';

describe('AddEditGstr2Component', () => {
  let component: AddEditGstr2Component;
  let fixture: ComponentFixture<AddEditGstr2Component>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AddEditGstr2Component ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AddEditGstr2Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

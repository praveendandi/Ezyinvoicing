import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Gstr2Component } from './gstr2.component';

describe('Gstr2Component', () => {
  let component: Gstr2Component;
  let fixture: ComponentFixture<Gstr2Component>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ Gstr2Component ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(Gstr2Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

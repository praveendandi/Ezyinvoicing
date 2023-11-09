import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Gstr1Component } from './gstr1.component';

describe('Gstr1Component', () => {
  let component: Gstr1Component;
  let fixture: ComponentFixture<Gstr1Component>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ Gstr1Component ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(Gstr1Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

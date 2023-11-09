import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AmendInvoicesComponent } from './amend-invoices.component';

describe('AmendInvoicesComponent', () => {
  let component: AmendInvoicesComponent;
  let fixture: ComponentFixture<AmendInvoicesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AmendInvoicesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AmendInvoicesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

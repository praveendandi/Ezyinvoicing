import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreditInvoicesComponent } from './credit-invoices.component';

describe('CreditInvoicesComponent', () => {
  let component: CreditInvoicesComponent;
  let fixture: ComponentFixture<CreditInvoicesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreditInvoicesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CreditInvoicesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

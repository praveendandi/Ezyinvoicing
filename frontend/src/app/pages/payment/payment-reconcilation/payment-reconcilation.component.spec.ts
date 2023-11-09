import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PaymentReconcilationComponent } from './payment-reconcilation.component';

describe('PaymentReconcilationComponent', () => {
  let component: PaymentReconcilationComponent;
  let fixture: ComponentFixture<PaymentReconcilationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PaymentReconcilationComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PaymentReconcilationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

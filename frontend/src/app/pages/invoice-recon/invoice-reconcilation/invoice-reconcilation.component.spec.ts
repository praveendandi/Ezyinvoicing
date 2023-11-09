import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InvoiceReconcilationComponent } from './invoice-reconcilation.component';

describe('InvoiceReconcilationComponent', () => {
  let component: InvoiceReconcilationComponent;
  let fixture: ComponentFixture<InvoiceReconcilationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ InvoiceReconcilationComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(InvoiceReconcilationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

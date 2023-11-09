import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InvoiceReconcilationListComponent } from './invoice-reconcilation-list.component';

describe('InvoiceReconcilationListComponent', () => {
  let component: InvoiceReconcilationListComponent;
  let fixture: ComponentFixture<InvoiceReconcilationListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ InvoiceReconcilationListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(InvoiceReconcilationListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

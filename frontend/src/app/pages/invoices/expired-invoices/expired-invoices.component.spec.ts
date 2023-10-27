import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExpiredInvoicesComponent } from './expired-invoices.component';

describe('ExpiredInvoicesComponent', () => {
  let component: ExpiredInvoicesComponent;
  let fixture: ComponentFixture<ExpiredInvoicesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExpiredInvoicesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExpiredInvoicesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

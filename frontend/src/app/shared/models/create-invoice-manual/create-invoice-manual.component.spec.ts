import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateInvoiceManualComponent } from './create-invoice-manual.component';

describe('CreateInvoiceManualComponent', () => {
  let component: CreateInvoiceManualComponent;
  let fixture: ComponentFixture<CreateInvoiceManualComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateInvoiceManualComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CreateInvoiceManualComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UploadInvoicesComponent } from './upload-invoices.component';

describe('UploadInvoicesComponent', () => {
  let component: UploadInvoicesComponent;
  let fixture: ComponentFixture<UploadInvoicesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UploadInvoicesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(UploadInvoicesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

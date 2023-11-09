import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BulkUploadExcelProgressbarComponent } from './bulk-upload-excel-progressbar.component';

describe('BulkUploadExcelProgressbarComponent', () => {
  let component: BulkUploadExcelProgressbarComponent;
  let fixture: ComponentFixture<BulkUploadExcelProgressbarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BulkUploadExcelProgressbarComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BulkUploadExcelProgressbarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FileuploadProgressbarComponent } from './fileupload-progressbar.component';

describe('FileuploadProgressbarComponent', () => {
  let component: FileuploadProgressbarComponent;
  let fixture: ComponentFixture<FileuploadProgressbarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FileuploadProgressbarComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FileuploadProgressbarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

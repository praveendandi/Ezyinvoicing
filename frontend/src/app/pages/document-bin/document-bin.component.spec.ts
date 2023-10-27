import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DocumentBinComponent } from './document-bin.component';

describe('DocumentBinComponent', () => {
  let component: DocumentBinComponent;
  let fixture: ComponentFixture<DocumentBinComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DocumentBinComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DocumentBinComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeletedDocumentsComponent } from './deleted-documents.component';

describe('DeletedDocumentsComponent', () => {
  let component: DeletedDocumentsComponent;
  let fixture: ComponentFixture<DeletedDocumentsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DeletedDocumentsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DeletedDocumentsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

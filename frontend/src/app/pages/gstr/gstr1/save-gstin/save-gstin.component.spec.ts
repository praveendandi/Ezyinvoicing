import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SaveGstinComponent } from './save-gstin.component';

describe('SaveGstinComponent', () => {
  let component: SaveGstinComponent;
  let fixture: ComponentFixture<SaveGstinComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SaveGstinComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SaveGstinComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

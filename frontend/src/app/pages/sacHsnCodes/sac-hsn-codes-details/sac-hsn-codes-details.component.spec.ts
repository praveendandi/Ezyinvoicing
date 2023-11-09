import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SacHsnCodesDetailsComponent } from './sac-hsn-codes-details.component';

describe('SacHsnCodesDetailsComponent', () => {
  let component: SacHsnCodesDetailsComponent;
  let fixture: ComponentFixture<SacHsnCodesDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SacHsnCodesDetailsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SacHsnCodesDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

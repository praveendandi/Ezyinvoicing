import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SacHsnCodesComponent } from './sac-hsn-codes.component';

describe('SacHsnCodesComponent', () => {
  let component: SacHsnCodesComponent;
  let fixture: ComponentFixture<SacHsnCodesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SacHsnCodesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SacHsnCodesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

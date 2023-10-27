import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SacHsnOutwardComponent } from './sac-hsn-outward.component';

describe('SacHsnOutwardComponent', () => {
  let component: SacHsnOutwardComponent;
  let fixture: ComponentFixture<SacHsnOutwardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SacHsnOutwardComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SacHsnOutwardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

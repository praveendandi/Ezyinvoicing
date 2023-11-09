import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdditinalInfoComponent } from './additinal-info.component';

describe('AdditinalInfoComponent', () => {
  let component: AdditinalInfoComponent;
  let fixture: ComponentFixture<AdditinalInfoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AdditinalInfoComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AdditinalInfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

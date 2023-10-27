import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GstrComponent } from './gstr.component';

describe('GstrComponent', () => {
  let component: GstrComponent;
  let fixture: ComponentFixture<GstrComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GstrComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(GstrComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

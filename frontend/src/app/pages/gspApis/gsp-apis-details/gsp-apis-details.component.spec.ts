import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GspApisDetailsComponent } from './gsp-apis-details.component';

describe('GspApisDetailsComponent', () => {
  let component: GspApisDetailsComponent;
  let fixture: ComponentFixture<GspApisDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GspApisDetailsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(GspApisDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

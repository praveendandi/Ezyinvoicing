import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NillRatedComponent } from './nill-rated.component';

describe('NillRatedComponent', () => {
  let component: NillRatedComponent;
  let fixture: ComponentFixture<NillRatedComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ NillRatedComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(NillRatedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

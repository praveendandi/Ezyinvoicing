import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GspApisComponent } from './gsp-apis.component';

describe('GspApisComponent', () => {
  let component: GspApisComponent;
  let fixture: ComponentFixture<GspApisComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GspApisComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(GspApisComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

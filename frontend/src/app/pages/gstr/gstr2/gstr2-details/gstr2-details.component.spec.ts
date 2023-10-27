import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Gstr2DetailsComponent } from './gstr2-details.component';

describe('Gstr2DetailsComponent', () => {
  let component: Gstr2DetailsComponent;
  let fixture: ComponentFixture<Gstr2DetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ Gstr2DetailsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(Gstr2DetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TempSacLineComponent } from './temp-sac-line.component';

describe('TempSacLineComponent', () => {
  let component: TempSacLineComponent;
  let fixture: ComponentFixture<TempSacLineComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TempSacLineComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TempSacLineComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

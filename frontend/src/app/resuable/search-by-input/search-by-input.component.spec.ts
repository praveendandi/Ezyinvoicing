import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SearchByInputComponent } from './search-by-input.component';

describe('SearchByInputComponent', () => {
  let component: SearchByInputComponent;
  let fixture: ComponentFixture<SearchByInputComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SearchByInputComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SearchByInputComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

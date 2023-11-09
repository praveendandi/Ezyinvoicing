import { ComponentFixture, TestBed } from '@angular/core/testing';

import { IpPrintersComponent } from './ip-printers.component';

describe('IpPrintersComponent', () => {
  let component: IpPrintersComponent;
  let fixture: ComponentFixture<IpPrintersComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ IpPrintersComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(IpPrintersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

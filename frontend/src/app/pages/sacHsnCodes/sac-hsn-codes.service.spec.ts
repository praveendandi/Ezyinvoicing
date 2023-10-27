import { TestBed } from '@angular/core/testing';

import { SacHsnCodesService } from './sac-hsn-codes.service';

describe('SacHsnCodesService', () => {
  let service: SacHsnCodesService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SacHsnCodesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

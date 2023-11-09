import { TestBed } from '@angular/core/testing';

import { ApiCallInterceptor } from './api-call.interceptor';

describe('ApiCallInterceptor', () => {
  beforeEach(() => TestBed.configureTestingModule({
    providers: [
      ApiCallInterceptor
      ]
  }));

  it('should be created', () => {
    const interceptor: ApiCallInterceptor = TestBed.inject(ApiCallInterceptor);
    expect(interceptor).toBeTruthy();
  });
});

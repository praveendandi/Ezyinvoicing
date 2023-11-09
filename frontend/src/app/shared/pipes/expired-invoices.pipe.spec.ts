import { ExpiredInvoicesPipe } from './expired-invoices.pipe';

describe('ExpiredInvoicesPipe', () => {
  it('create an instance', () => {
    const pipe = new ExpiredInvoicesPipe();
    expect(pipe).toBeTruthy();
  });
});

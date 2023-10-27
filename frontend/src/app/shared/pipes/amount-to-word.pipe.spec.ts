import { AmountToWordPipe } from './amount-to-word.pipe';

describe('AmountToWordPipe', () => {
  it('create an instance', () => {
    const pipe = new AmountToWordPipe();
    expect(pipe).toBeTruthy();
  });
});

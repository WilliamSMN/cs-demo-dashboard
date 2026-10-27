import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TimingHistogram } from './timing-histogram';

describe('TimingHistogram', () => {
  let component: TimingHistogram;
  let fixture: ComponentFixture<TimingHistogram>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TimingHistogram],
    }).compileComponents();

    fixture = TestBed.createComponent(TimingHistogram);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

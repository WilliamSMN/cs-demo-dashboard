import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TradesTable } from './trades-table';

describe('TradesTable', () => {
  let component: TradesTable;
  let fixture: ComponentFixture<TradesTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TradesTable],
    }).compileComponents();

    fixture = TestBed.createComponent(TradesTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

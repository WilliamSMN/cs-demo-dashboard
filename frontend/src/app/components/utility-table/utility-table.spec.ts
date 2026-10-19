import { ComponentFixture, TestBed } from '@angular/core/testing';
import { UtilityTable } from './utility-table';

describe('UtilityTable', () => {
  let component: UtilityTable;
  let fixture: ComponentFixture<UtilityTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UtilityTable],
    }).compileComponents();

    fixture = TestBed.createComponent(UtilityTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

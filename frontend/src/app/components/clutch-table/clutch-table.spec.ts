import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ClutchTable } from './clutch-table';

describe('ClutchTable', () => {
  let component: ClutchTable;
  let fixture: ComponentFixture<ClutchTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ClutchTable],
    }).compileComponents();

    fixture = TestBed.createComponent(ClutchTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

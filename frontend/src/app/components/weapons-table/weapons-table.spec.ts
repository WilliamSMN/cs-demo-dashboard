import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WeaponsTable } from './weapons-table';

describe('WeaponsTable', () => {
  let component: WeaponsTable;
  let fixture: ComponentFixture<WeaponsTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WeaponsTable],
    }).compileComponents();

    fixture = TestBed.createComponent(WeaponsTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

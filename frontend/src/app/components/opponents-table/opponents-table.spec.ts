import { ComponentFixture, TestBed } from '@angular/core/testing';
import { OpponentsTable } from './opponents-table';

describe('OpponentsTable', () => {
  let component: OpponentsTable;
  let fixture: ComponentFixture<OpponentsTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OpponentsTable],
    }).compileComponents();

    fixture = TestBed.createComponent(OpponentsTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

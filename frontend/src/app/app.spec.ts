import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { App } from './app';

describe('App', () => {
  it('affiche le statut du backend', async () => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    const fixture = TestBed.createComponent(App);

    TestBed.inject(HttpTestingController)
      .expectOne('http://127.0.0.1:8000/health')
      .flush({ status: 'ok' });
    await fixture.whenStable();

    expect(fixture.nativeElement.textContent).toContain('Backend : ok');
  });
});

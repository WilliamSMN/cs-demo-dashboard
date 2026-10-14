import { HttpInterceptorFn } from '@angular/common/http';
import { API_URL } from '../config';

export const credentialsInterceptor: HttpInterceptorFn = (req, next) => {
  if (req.url.startsWith(API_URL)) {
    return next(req.clone({ withCredentials: true }));
  }
  return next(req);
};

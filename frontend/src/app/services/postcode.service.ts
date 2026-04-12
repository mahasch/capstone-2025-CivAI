// src/app/services/postcode.service.ts
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
// import { encryptData } from '../utils/crypto.util';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class PostcodeService {
  private readonly apiUrl = 'https://your-backend/api/postcode';

  constructor(private http: HttpClient) {}

  sendPostcode(postcode: string): Observable<any> {

    return this.http.post(this.apiUrl, {
      payload: postcode,
    });
  }
}

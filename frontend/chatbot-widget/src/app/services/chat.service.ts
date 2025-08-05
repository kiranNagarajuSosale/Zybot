import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ChatQuery } from '../Model/request';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private domContextEnabled = false;

  constructor(private http: HttpClient) { }
  
  setDomContextEnabled(enabled: boolean) {
    this.domContextEnabled = enabled;
  }

  isDomContextEnabled(): boolean {
    return this.domContextEnabled;
  }

  sendMessage(payload: ChatQuery): Observable<any> {
    console.log("Sending chat payload:", payload);
    // Include DOM context state in the payload
    const finalPayload = {
      ...payload,
      domContextEnabled: this.domContextEnabled
    };
    return this.http.post<any>(environment.chatUrl, finalPayload);
  }
}


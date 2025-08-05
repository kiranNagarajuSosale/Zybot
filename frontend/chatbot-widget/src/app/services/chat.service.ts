import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ChatQuery } from '../Model/request';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private chatUrl = 'https://127.0.0.1:9443/chat';

  constructor(private http: HttpClient) {}

  sendMessage(payload: ChatQuery): Observable<any> {
    console.log("Sending chat payload:", payload);
    return this.http.post<any>(this.chatUrl, payload);
  }
}


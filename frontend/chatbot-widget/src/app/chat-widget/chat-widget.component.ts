import { Component, ChangeDetectorRef } from '@angular/core';
import { ChatService } from '../services/chat.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatResponse } from '../Model/response';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { ChatQuery } from '../Model/request';

@Component({
  selector: 'app-chat-widget',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat-widget.component.html',
  styleUrls: ['./chat-widget.component.css']
})
export class ChatWidgetComponent {
  domContextEnabled = false;
  isOpen = false;
  userInput = '';
  messages: { text: string | SafeHtml, sender: 'user' | 'bot', format?: string }[] = [];

  models: string[] = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-2.5-pro'];
  selectedModel: string = this.models[0]; // Default to 'gemini-2.0-flash'

  roles: string[] = ['developer', 'tester', 'user'];
  selectedRole: string = this.roles[0]; // Default to 'developer'

  constructor(private chatService: ChatService, private cdr: ChangeDetectorRef, private sanitizer: DomSanitizer) { }

  toggleChat() {
    this.isOpen = !this.isOpen;
  }

  isLoading = false;

  onModelChange(event: any) {
    this.selectedModel = event.target.value;
  }

  toggleDomContext() {
    this.domContextEnabled = !this.domContextEnabled;
    this.chatService.setDomContextEnabled(this.domContextEnabled);

    if (this.domContextEnabled) {
      const domText = document.body.innerText.slice(0, 500);
    }
  }

  sendMessage() {
    const message = this.userInput.trim();
    if (!message) return;

    this.messages.push({ text: message, sender: 'user' });
    this.userInput = '';
    this.isLoading = true;
    let domContext = '';
    if (this.domContextEnabled) {
      domContext = document.body.innerText.slice(0, 2000); // :) for better context upto 2000 character for now
    }

    let traceContext = '';
    if (this.domContextEnabled) {
      try {
        const currentUrl = window.location.href;
        const timestamp = new Date().toISOString();
        // Get user agent
        const userAgent = navigator.userAgent;

        traceContext = JSON.stringify({
          url: currentUrl,
          timestamp: timestamp,
          userAgent: userAgent,
          screenSize: {
            width: window.innerWidth,
            height: window.innerHeight
          }
        });
      } catch (error) {
        console.error('Error capturing trace context:', error);
      }
    }
    const requestPayload: ChatQuery = {
      question: message,
      role: this.selectedRole,
      dom_context: domContext,
      trace_context: traceContext,
      model: this.selectedModel
    };
    console.log('Request Payload:', requestPayload);
    this.chatService.sendMessage(requestPayload).subscribe({
      next: (response: ChatResponse) => {
        if (response.answer) {
          console.log("Chatbot response:", response);
          console.log("Response format:", response.format);
          console.log("Response answer length:", response.answer.length);
          console.log("First 100 chars:", response.answer.substring(0, 100));

          let messageText: string | SafeHtml = response.answer;

          // If it's HTML format, sanitize it for safety
          if (response.format === 'html') {
            messageText = this.sanitizer.bypassSecurityTrustHtml(response.answer);
            console.log("HTML sanitized successfully");
          }

          this.messages.push({
            text: messageText,
            sender: 'bot',
            format: response.format
          });
        }
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.messages.push({ text: 'Error: Unable to get response from bot.', sender: 'bot' });
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }
}

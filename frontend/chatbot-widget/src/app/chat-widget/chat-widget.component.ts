import { Component, ChangeDetectorRef } from '@angular/core';
import { ChatService } from '../services/chat.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatResponse } from '../Model/response';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Component({
  selector: 'app-chat-widget',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat-widget.component.html',
  styleUrls: ['./chat-widget.component.css']
})
export class ChatWidgetComponent {
  isOpen = false;
  userInput = '';
  messages: { text: string | SafeHtml, sender: 'user' | 'bot', format?: string }[] = [];

  models: string[] = ['gemini-2.0-flash','gemini-2.5-flash', 'gemini-2.5-pro'];
  selectedModel: string = this.models[0]; // Default to 'gemini-2.0-flash'

  roles: string[] = ['developer', 'tester', 'user'];
  selectedRole: string = this.roles[0]; // Default to 'developer'

  constructor(private chatService: ChatService, private cdr: ChangeDetectorRef, private sanitizer: DomSanitizer) {}

  toggleChat() {
    this.isOpen = !this.isOpen;
  }

  isLoading = false;

  onModelChange(event: any) {
    this.selectedModel = event.target.value;
    // Optionally notify backend or chat service about model change
  }

  sendMessage() {
    const message = this.userInput.trim();
    if (!message) return;

    this.messages.push({ text: message, sender: 'user' });
    this.userInput = '';
    this.isLoading = true;

    this.chatService.sendMessage({
      question: message,
      role: this.selectedRole,
      dom_context: '',
      trace_context: '',
      model: this.selectedModel
    }).subscribe({
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


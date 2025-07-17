import { Component, ChangeDetectorRef } from '@angular/core';
import { ChatService } from '../services/chat.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatResponse } from '../Model/response';

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
  messages: { text: string, sender: 'user' | 'bot' }[] = [];

  constructor(private chatService: ChatService, private cdr: ChangeDetectorRef) {}

  toggleChat() {
    this.isOpen = !this.isOpen;
  }

  isLoading = false;

  sendMessage() {
    const message = this.userInput.trim();
    if (!message) return;

    this.messages.push({ text: message, sender: 'user' });
    this.userInput = '';
    this.isLoading = true;

    this.chatService.sendMessage({
      question: message,
      role: 'user',
      dom_context: '',
      trace_context: ''
    }).subscribe({
      next: (response: ChatResponse) => {
        if (response.answer) {
          this.messages.push({ text: response.answer, sender: 'bot' });
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


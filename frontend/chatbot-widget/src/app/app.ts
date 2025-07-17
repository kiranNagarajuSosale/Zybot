import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ChatWidgetComponent } from './chat-widget/chat-widget.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ChatWidgetComponent], // ✅ Add it here
  template: `<app-chat-widget></app-chat-widget>`, // ✅ Use the selector

})
export class App {
  protected readonly title = signal('chatbot-widget');
  // selector: 'app-root',
  // imports: [RouterOutlet],
  // standalone: true,
  // template: `<app-chat-widget></app-chat-widget>`, 
  // styleUrl: './app.css'
}

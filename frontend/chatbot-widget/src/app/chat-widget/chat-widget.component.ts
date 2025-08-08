import { Component, ChangeDetectorRef, AfterViewChecked, ElementRef, ViewChild } from '@angular/core';
import { ChatService } from '../services/chat.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatResponse } from '../Model/response';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { ChatQuery, DomContextData } from '../Model/request';

@Component({
  selector: 'app-chat-widget',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat-widget.component.html',
  styleUrls: ['./chat-widget.component.css']
})
export class ChatWidgetComponent implements AfterViewChecked {
  @ViewChild('chatBody') private chatBodyRef!: ElementRef;
  private scrollToBottom = false;
  
  domContextEnabled = false;
  isOpen = false;
  userInput = '';
  messages: { text: string | SafeHtml, sender: 'user' | 'bot', format?: string }[] = [];
  selectedDomContent: string | null = null;
  selectedDomElement: HTMLElement | null = null;
  selectedDomData: DomContextData | null = null;
  private documentClickListener: ((event: MouseEvent) => void) | null = null;
  private mouseMoveListener: ((event: MouseEvent) => void) | null = null;

  models: string[] = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-2.5-pro'];
  selectedModel: string = this.models[0]; // Default to 'gemini-2.0-flash'

  roles: string[] = ['developer', 'tester', 'user'];
  selectedRole: string = this.roles[0]; // Default to 'developer'

  constructor(private chatService: ChatService, private cdr: ChangeDetectorRef, private sanitizer: DomSanitizer) { }

  ngAfterViewChecked() {
    if (this.scrollToBottom) {
      this.scrollChatToBottom();
      this.scrollToBottom = false;
    }
  }

  private scrollChatToBottom(): void {
    try {
      const chatBody = this.chatBodyRef?.nativeElement;
      if (chatBody) {
        chatBody.scrollTop = chatBody.scrollHeight;
      }
    } catch (err) {
      console.error('Error scrolling chat to bottom:', err);
    }
  }

  toggleChat() {
    this.isOpen = !this.isOpen;
    if (this.isOpen) {
      // Schedule scrolling for after view is updated
      setTimeout(() => this.scrollToBottom = true, 100);
    }
  }

  isLoading = false;

  onModelChange(event: any) {
    this.selectedModel = event.target.value;
  }
  
  clearChat() {
    this.messages = [];
    this.selectedDomContent = null;
    this.selectedDomElement = null;
    this.selectedDomData = null;
    
    // Scroll to top after clearing chat
    if (this.chatBodyRef?.nativeElement) {
      this.chatBodyRef.nativeElement.scrollTop = 0;
    }
  }

  toggleDomContext() {
    this.domContextEnabled = !this.domContextEnabled;
    this.chatService.setDomContextEnabled(this.domContextEnabled);
    this.selectedDomContent = null;

    if (this.domContextEnabled) {
      const chatWindow = document.querySelector('.chat-window');
      chatWindow?.classList.add('closing');
      
      setTimeout(() => {
        this.isOpen = false;
        this.setupDomClickListener();
        this.addSelectableStyles();
      }, 300);
    } else {
      this.removeDomClickListener();
      this.removeSelectableStyles();
    }
  }

  private addSelectableStyles() {
    document.body.style.cursor = 'pointer';
    const elements = document.body.getElementsByTagName('*');
    for (let i = 0; i < elements.length; i++) {
      const element = elements[i] as HTMLElement;
      if (!this.isElementPartOfWidget(element)) {
        element.classList.add('selectable-element');
      }
    }
  }

  private removeSelectableStyles() {
    document.body.style.cursor = '';
    const elements = document.getElementsByClassName('selectable-element');
    while (elements.length > 0) {
      elements[0].classList.remove('selectable-element');
    }
  }

  private setupDomClickListener() {
    if (!this.documentClickListener) {
      this.mouseMoveListener = (event: MouseEvent) => {
        if (this.domContextEnabled) {
          const target = event.target as HTMLElement;
          if (!this.isElementPartOfWidget(target)) {
            this.removeHighlightBoxes();
            this.createHighlightBox(target);
          }
        }
      };
      
      document.addEventListener('mousemove', this.mouseMoveListener, true);
      
      this.documentClickListener = (event: MouseEvent) => {
        if (this.domContextEnabled) {
          const target = event.target as HTMLElement;
          if (!this.isElementPartOfWidget(target)) {
            event.preventDefault();
            event.stopPropagation();
            
            const rect = target.getBoundingClientRect();
            const highlightBox = document.createElement('div');
            highlightBox.className = 'element-highlight-box';
            highlightBox.style.position = 'fixed';
            highlightBox.style.top = rect.top + 'px';
            highlightBox.style.left = rect.left + 'px';
            highlightBox.style.width = rect.width + 'px';
            highlightBox.style.height = rect.height + 'px';
            highlightBox.style.border = '2px solid #ff5722';
            highlightBox.style.backgroundColor = 'rgba(255, 87, 34, 0.1)';
            highlightBox.style.zIndex = '9999';
            document.body.appendChild(highlightBox);
            
            // Store the selected element for later use
            this.selectedDomElement = target;
            this.selectedDomContent = target.innerText.trim();
            
            // Capture comprehensive DOM information
            this.captureDomData(target);
            
            setTimeout(() => {
              document.body.removeChild(highlightBox);
              this.removeHighlightBoxes();
              
              this.isOpen = true;
              this.domContextEnabled = false;
              this.chatService.setDomContextEnabled(false);
              this.removeDomClickListener();
              this.removeSelectableStyles();
              
              // Schedule scrolling after DOM context is displayed
              setTimeout(() => this.scrollToBottom = true, 200);
            }, 500);
          }
        }
      };
      document.addEventListener('click', this.documentClickListener, true);
    }
  }
  
  private createHighlightBox(element: HTMLElement) {
    const rect = element.getBoundingClientRect();
    
    // Create the highlight box with fixed positioning relative to viewport
    const highlightBox = document.createElement('div');
    highlightBox.className = 'element-highlight-box';
    highlightBox.style.position = 'fixed';
    highlightBox.style.top = rect.top + 'px';
    highlightBox.style.left = rect.left + 'px';
    highlightBox.style.width = rect.width + 'px';
    highlightBox.style.height = rect.height + 'px';
    document.body.appendChild(highlightBox);
    
    // Create element label with tag name
    const label = document.createElement('div');
    label.className = 'element-label';
    label.style.position = 'fixed';
    label.textContent = element.tagName.toLowerCase();
    
    if (element.className && typeof element.className === 'string' && element.className.trim()) {
      const classNames = element.className.split(' ')[0];
      label.textContent += '.' + classNames;
    }
    
    if (element.id) {
      label.textContent += '#' + element.id;
    }
    
    // Position the label above the element when possible
    if (rect.top > 40) {
      label.style.top = (rect.top - 20) + 'px';
    } else {
      label.style.top = rect.top + 'px';
    }
    label.style.left = rect.left + 'px';
    document.body.appendChild(label);
    
    highlightBox.dataset['forDomContext'] = 'true';
    label.dataset['forDomContext'] = 'true';
  }
  
  private removeHighlightBoxes() {
    const highlights = document.querySelectorAll('[data-for-dom-context="true"]');
    highlights.forEach(el => el.parentNode?.removeChild(el));
  }

  private removeDomClickListener() {
    if (this.documentClickListener) {
      document.removeEventListener('click', this.documentClickListener, true);
      this.documentClickListener = null;
    }
    
    if (this.mouseMoveListener) {
      document.removeEventListener('mousemove', this.mouseMoveListener, true);
      this.mouseMoveListener = null;
    }
    
    this.removeHighlightBoxes();
  }

  private captureDomData(element: HTMLElement): void {
    if (!element) return;

    // Get computed styles for the element
    const computedStyle = window.getComputedStyle(element);
    const importantStyles: Record<string, string> = {};
    
    // Capture important styles that may be relevant for context
    const stylesToCapture = [
      'color', 'backgroundColor', 'fontSize', 'fontWeight', 
      'display', 'position', 'visibility', 'opacity',
      'margin', 'padding', 'border', 'width', 'height'
    ];
    
    stylesToCapture.forEach(style => {
      importantStyles[style] = computedStyle.getPropertyValue(style);
    });

    // Get all attributes
    const attributes: Record<string, string> = {};
    for (let i = 0; i < element.attributes.length; i++) {
      const attr = element.attributes[i];
      attributes[attr.name] = attr.value;
    }

    // Get XPath
    const xpath = this.getXPathForElement(element);
    
    const rect = element.getBoundingClientRect();

    // Create the dom context data object
    this.selectedDomData = {
      innerText: element.innerText,
      innerHTML: element.innerHTML,
      tagName: element.tagName.toLowerCase(),
      id: element.id || undefined,
      className: element.className || undefined,
      attributes: attributes,
      computedStyles: importantStyles,
      xpath: xpath,
      dimensions: {
        width: rect.width,
        height: rect.height,
        top: rect.top,
        left: rect.left
      }
    };
  }

  private getXPathForElement(element: HTMLElement): string {
    if (!element) return '';
    
    // Check if the element has an ID
    if (element.id) {
      return `//*[@id="${element.id}"]`;
    }
    
    // If the element is the document body, return the path
    if (element === document.body) {
      return '/html/body';
    }
    
    // Variables for iteration
    let currentNode = element;
    let path = '';
    
    // Traverse the DOM upwards until we reach the body
    while (currentNode && currentNode !== document.body) {
      let nodeName = currentNode.nodeName.toLowerCase();
      let nodePosition = 1;
      
      // Get all siblings of the same type
      if (currentNode.parentNode) {
        let siblings = currentNode.parentNode.childNodes;
        let count = 0;
        for (let i = 0; i < siblings.length; i++) {
          let siblingNode = siblings[i];
          if (
            siblingNode.nodeType === currentNode.nodeType &&
            (siblingNode as HTMLElement).nodeName.toLowerCase() === nodeName
          ) {
            count++;
          }
          if (siblingNode === currentNode) {
            nodePosition = count;
            break;
          }
        }
      }
      
      // Add to the path
      path = `/${nodeName}[${nodePosition}]${path}`;
      
      // Move up to the parent
      currentNode = currentNode.parentElement as HTMLElement;
    }
    
    return `/html/body${path}`;
  }

  private isElementPartOfWidget(element: HTMLElement): boolean {
    const widgetElement = document.querySelector('app-chat-widget');
    return widgetElement?.contains(element) || false;
  }

  clearDomDetails() {
    // Clear DOM details from the component
    this.selectedDomContent = null;
    this.selectedDomElement = null;
    this.selectedDomData = null;
    
    // Add a confirmation message to the chat
    this.messages.push({
      text: "DOM details have been cleared",
      sender: 'bot'
    });
    
    // Scroll to bottom after clearing DOM data
    setTimeout(() => this.scrollToBottom = true, 100);
  }

  sendMessage() {
    const message = this.userInput.trim();
    if (!message) return;

    this.messages.push({ text: message, sender: 'user' });
    this.userInput = '';
    this.isLoading = true;
    
    // Scroll to bottom after adding user message
    this.scrollToBottom = true;
    
    let traceContext = '';
    if (this.selectedDomContent) {
      try {
        const currentUrl = window.location.href;
        const timestamp = new Date().toISOString();
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
      dom_context: this.selectedDomData || undefined,
      trace_context: traceContext,
      model: this.selectedModel
    };
    
    this.chatService.sendMessage(requestPayload).subscribe({
      next: (response: ChatResponse) => {
        if (response.answer) {
          let messageText: string | SafeHtml = response.answer;

          if (response.format === 'html') {
            messageText = this.sanitizer.bypassSecurityTrustHtml(response.answer);
          }

          this.messages.push({
            text: messageText,
            sender: 'bot',
            format: response.format
          });
        }
        this.isLoading = false;
        this.cdr.detectChanges();
        
        // Scroll to bottom after receiving and rendering the response
        setTimeout(() => this.scrollToBottom = true, 100);
      },
      error: () => {
        this.messages.push({ text: 'Error: Unable to get response from bot.', sender: 'bot' });
        this.isLoading = false;
        this.cdr.detectChanges();
        
        // Scroll to bottom even if there's an error
        setTimeout(() => this.scrollToBottom = true, 100);
      }
    });
  }
}

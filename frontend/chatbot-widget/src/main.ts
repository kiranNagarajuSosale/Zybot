import { createApplication } from '@angular/platform-browser';
import { createCustomElement } from '@angular/elements';
import { ChatWidgetComponent } from './app/chat-widget/chat-widget.component';
import { importProvidersFrom } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import 'zone.js';

(async () => {
  const app = await createApplication({
    providers: [
      importProvidersFrom(HttpClientModule)
    ]
  });

  const customEl = createCustomElement(ChatWidgetComponent, {
    injector: app.injector,
  });

  customElements.define('chat-widget', customEl);
})();

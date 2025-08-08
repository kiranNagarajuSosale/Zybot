export interface DomContextData {
  innerText: string;
  innerHTML: string;
  tagName: string;
  id?: string;
  className?: string;
  attributes?: Record<string, string>;
  computedStyles?: Record<string, string>;
  xpath?: string;
  dimensions?: {
    width: number;
    height: number;
    top: number;
    left: number;
  };
}

export interface ChatQuery {
  question: string;
  role: string;
  dom_context?: DomContextData;
  trace_context?: string;
  model?: string;
}
export interface ChatQuery {
  question: string;
  role: string;
  dom_context?: string;
  trace_context?: string;
  model?: string;
}
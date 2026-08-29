export interface User {
  id?: string;
  name: string;
  email: string;
  role: 'student' | 'admin';
}

export interface SourceMetadata {
  document_title: string;
  page_number?: number;
  snippet: string;
  relevance_score: number;
}

export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceMetadata[];
  feedback?: 'up' | 'down' | null;
  created_at?: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
}

export interface DocumentItem {
  id: string;
  title: string;
  filename: string;
  department?: string;
  collection?: string;
  status: 'processing' | 'processed' | 'failed';
  version: number;
  created_at: string;
}

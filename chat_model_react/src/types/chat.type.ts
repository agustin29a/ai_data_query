import type { ResultData, ChartData } from './api.type';

export interface SendMessageParams {
  content: string;
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export interface ChatSession {
  _id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
  messages?: Message[]; 
}

export interface ChatState {
  _id: string;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  currentSessionId: string | null;
  isSidebarCollapsed: boolean;
}

export interface SendMessageParams {
  content: string;
  sessionId?: string;
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export interface Content {
  query_sql: string;
  chart_base64: string;
  query_result:  ResultData;
}

export interface Message {
  _id: string;
  content?: string | Content;
  isUser: boolean;
  timestamp: Date;
  sql?: string;
  role?: string;
  chartData?: ChartData;
  resultData?: ResultData;
}

export interface QueryResult {
  columns: string[];
  data: string[];
}

export interface MessageSession {
  _id: string;
  messages: Message[];
}
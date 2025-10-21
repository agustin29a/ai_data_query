import type { ChatSession, MessageSession } from '../types/chat.type';

const SESSIONS_API_BASE_URL = import.meta.env.VITE_SESSIONS_API_BASE_URL;

export class SessionService {
  static async getSessions(): Promise<ChatSession[]> {
    const response = await fetch(`${SESSIONS_API_BASE_URL}?sortByDate=desc`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return response.json();
  }

  static async createSession(title: string): Promise<ChatSession> {
    const response = await fetch(`${SESSIONS_API_BASE_URL}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return response.json();
  }

  static async getSessionMessages(sessionId: string): Promise<MessageSession> {
    const response = await fetch(`${SESSIONS_API_BASE_URL}/${sessionId}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return response.json();
  }

  static async deleteSession(sessionId: string): Promise<void> {
    const response = await fetch(`${SESSIONS_API_BASE_URL}/${sessionId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
  }
}
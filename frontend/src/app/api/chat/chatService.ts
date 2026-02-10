/**
 * Chat Service for Todo App
 * Handles communication between frontend and backend chat API
 */

import { getToken } from '@/lib/auth';

interface ChatRequest {
  message: string;
  conversation_id?: string;
}

interface ChatResponse {
  response: string;
  conversation_id: string;
}

interface Conversation {
  id: string;
  user_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

interface Message {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  timestamp: string;
  metadata?: any;
}

interface ConversationWithMessages {
  conversation: Conversation;
  messages: Message[];
}

class ChatService {
  private baseUrl: string;

  constructor() {
    // Use the same environment variable pattern as other API services
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001';
  }

  /**
   * Send a message to the chat API
   */
  async sendMessage(message: string, conversationId?: string): Promise<ChatResponse> {
    try {
      const token = getToken();

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          message,
          conversation_id: conversationId
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Handle unauthorized access - possibly redirect to login
          localStorage.removeItem('userSession');
          window.location.href = '/login';
          throw new Error('Authentication required. Please log in.');
        }
        if (response.status === 429) {
          // Handle rate limit errors
          const errorData = await response.json().catch(() => ({ detail: 'Rate limit exceeded' }));
          throw new Error(errorData.detail || 'The AI service is temporarily rate-limited. Please try again in a few moments.');
        }
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `Failed to send message: ${response.statusText}`);
      }

      const data: ChatResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  /**
   * Get all conversations for the current user
   */
  async getConversations(): Promise<Conversation[]> {
    try {
      const token = getToken();

      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${this.baseUrl}/api/v1/chat/conversations`, {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Handle unauthorized access - possibly redirect to login
          localStorage.removeItem('userSession');
          window.location.href = '/login';
          throw new Error('Authentication required. Please log in.');
        }
        throw new Error(`Failed to get conversations: ${response.statusText}`);
      }

      const data: Conversation[] = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting conversations:', error);
      throw error;
    }
  }

  /**
   * Get a specific conversation with its messages
   */
  async getConversation(conversationId: string): Promise<ConversationWithMessages> {
    try {
      const token = getToken();

      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${this.baseUrl}/api/v1/chat/conversations/${conversationId}`, {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Handle unauthorized access - possibly redirect to login
          localStorage.removeItem('userSession');
          window.location.href = '/login';
          throw new Error('Authentication required. Please log in.');
        }
        throw new Error(`Failed to get conversation: ${response.statusText}`);
      }

      const data: ConversationWithMessages = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting conversation:', error);
      throw error;
    }
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: string): Promise<boolean> {
    try {
      const token = getToken();

      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${this.baseUrl}/api/v1/chat/conversations/${conversationId}`, {
        method: 'DELETE',
        headers,
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Handle unauthorized access - possibly redirect to login
          localStorage.removeItem('userSession');
          window.location.href = '/login';
          throw new Error('Authentication required. Please log in.');
        }
        throw new Error(`Failed to delete conversation: ${response.statusText}`);
      }

      return true;
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  }
}

export const chatService = new ChatService();

export type { ChatRequest, ChatResponse, Conversation, Message, ConversationWithMessages };
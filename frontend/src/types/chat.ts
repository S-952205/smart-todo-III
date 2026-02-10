// Chat-related TypeScript definitions

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  tool_calls?: Array<{
    tool_name: string;
    parameters: Record<string, any>;
  }>;
}

export interface Conversation {
  id: string;
  user_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface ConversationWithMessages {
  conversation: Conversation;
  messages: Message[];
}

export interface ChatHistory {
  conversations: Conversation[];
  currentConversation?: Conversation;
  messages: Message[];
}
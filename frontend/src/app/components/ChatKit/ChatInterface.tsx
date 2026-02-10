'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Message } from './Message';
import { MessageInput } from './MessageInput';
import { chatService, Conversation, Message as MessageType } from '@/app/api/chat/chatService';
import { useAuth } from '@/context/auth-context';

interface ChatInterfaceProps {
  conversationId?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ conversationId }) => {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>(conversationId);
  const { state } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversation from database on mount
  useEffect(() => {
    const loadMostRecentConversation = async () => {
      // If a specific conversation ID is provided, load that
      if (conversationId) {
        await loadConversation(conversationId);
        return;
      }

      // Otherwise, fetch the user's most recent conversation from database
      if (state.user?.id) {
        try {
          const conversations = await chatService.getConversations();

          // If user has conversations, load the most recent one
          if (conversations && conversations.length > 0) {
            // Sort by updated_at to get the most recent
            const sortedConversations = conversations.sort((a, b) =>
              new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
            );
            const mostRecent = sortedConversations[0];
            await loadConversation(mostRecent.id);
          }
        } catch (error) {
          console.error('Failed to load conversations from database:', error);
        }
      }
    };

    loadMostRecentConversation();
  }, [conversationId, state.user?.id]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversation = async (id: string) => {
    try {
      setIsLoading(true);
      const data = await chatService.getConversation(id);
      setMessages(data.messages);
      setCurrentConversationId(id);
    } catch (error) {
      console.error('Error loading conversation:', error);
      throw error; // Re-throw to handle in caller
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!message.trim() || !state.user?.id) return;

    // Add user message to UI immediately
    const userMessage: MessageType = {
      id: Date.now().toString(),
      conversation_id: currentConversationId || '',
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await chatService.sendMessage(message, currentConversationId);

      // Update conversation ID if it's a new conversation
      if (!currentConversationId) {
        setCurrentConversationId(response.conversation_id);
      }

      // Add assistant response to UI
      const assistantMessage: MessageType = {
        id: `assistant-${Date.now()}`,
        conversation_id: response.conversation_id,
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to UI with specific error details
      const errorContent = error instanceof Error
        ? error.message
        : 'Sorry, I encountered an error processing your request. Please try again.';

      const errorMessage: MessageType = {
        id: `error-${Date.now()}`,
        conversation_id: currentConversationId || '',
        role: 'assistant',
        content: errorContent,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-[60vh]">
        {messages.length > 0 ? (
          messages.map((msg) => (
            <Message
              key={msg.id}
              role={msg.role as 'user' | 'assistant'}
              content={msg.content}
              timestamp={new Date(msg.timestamp)}
            />
          ))
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            <p>Start a conversation by sending a message...</p>
          </div>
        )}
        {isLoading && (
          <Message
            role="assistant"
            content="Thinking..."
            timestamp={new Date()}
            isLoading={true}
          />
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t p-4 bg-gray-50 dark:bg-gray-700">
        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={isLoading || !state.user?.id}
        />
      </div>
    </div>
  );
};
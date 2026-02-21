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
  const [initialLoading, setInitialLoading] = useState(true);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>(conversationId);
  const { state } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversation from database on mount
  useEffect(() => {
    const loadMostRecentConversation = async () => {
      // If a specific conversation ID is provided, load that
      if (conversationId) {
        await loadConversation(conversationId);
        setInitialLoading(false);
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
        } finally {
          setInitialLoading(false);
        }
      } else {
        setInitialLoading(false);
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
    <div className="flex flex-col h-full bg-white dark:bg-gray-900 rounded-none shadow-xl overflow-hidden border border-[#BFC9D1]/40">
      {/* Chat Header */}
      <div className="px-6 py-4 bg-[#25343F] dark:bg-[#25343F] border-b border-[#BFC9D1]/20 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#FF5B5B] flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
            </svg>
          </div>
          <div>
            <h3 className="font-semibold text-white dark:text-white font-poppins">AI Assistant</h3>
            <p className="text-xs text-white/70 dark:text-gray-400 font-poppins font-light">Always here to help</p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600 scrollbar-track-transparent">
        {initialLoading ? (
          // Show loading state while checking for existing conversations
          <div className="flex items-center justify-center h-full">
            <Message
              role="assistant"
              content="Loading your conversation..."
              timestamp={new Date()}
              isLoading={true}
            />
          </div>
        ) : messages.length > 0 ? (
          // Show messages if they exist
          messages.map((msg) => (
            <Message
              key={msg.id}
              role={msg.role as 'user' | 'assistant'}
              content={msg.content}
              timestamp={new Date(msg.timestamp)}
            />
          ))
        ) : (
          // Show empty state only for new users with no chat history
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="w-16 h-16 mb-4 rounded-full bg-[#BFC9D1]/20 dark:bg-gray-700 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-[#25343F] dark:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <p className="text-[#25343F]/80 dark:text-gray-400 font-medium mb-2 font-poppins">Start a conversation</p>
            <p className="text-sm text-[#25343F]/60 dark:text-gray-500 font-poppins font-light">Ask me anything about your tasks or productivity!</p>
          </div>
        )}
        {isLoading && !initialLoading && (
          <Message
            role="assistant"
            content="Thinking..."
            timestamp={new Date()}
            isLoading={true}
          />
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <MessageInput
        onSendMessage={handleSendMessage}
        disabled={isLoading || !state.user?.id}
      />
    </div>
  );
};
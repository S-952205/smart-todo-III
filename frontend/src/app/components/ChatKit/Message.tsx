import React from 'react';
import { format } from 'date-fns';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isLoading?: boolean;
}

export const Message: React.FC<MessageProps> = ({ role, content, timestamp, isLoading = false }) => {
  const isUser = role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-xl p-4 ${
          isUser
            ? 'bg-blue-500 text-white rounded-br-none'
            : 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200 rounded-bl-none'
        }`}
      >
        <div className="whitespace-pre-wrap break-words">{content}</div>

        {isLoading && (
          <div className="flex space-x-2 pt-2">
            <div className="h-2 w-2 rounded-full bg-current opacity-40 animate-bounce"></div>
            <div className="h-2 w-2 rounded-full bg-current opacity-40 animate-bounce delay-75"></div>
            <div className="h-2 w-2 rounded-full bg-current opacity-40 animate-bounce delay-150"></div>
          </div>
        )}

        <div
          className={`text-xs mt-2 ${
            isUser ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
          }`}
        >
          {format(timestamp, 'HH:mm')}
        </div>
      </div>
    </div>
  );
};
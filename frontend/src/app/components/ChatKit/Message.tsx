import React from 'react';
import { format } from 'date-fns';
import { motion } from 'framer-motion';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isLoading?: boolean;
}

export const Message: React.FC<MessageProps> = ({ role, content, timestamp, isLoading = false }) => {
  const isUser = role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 shadow-sm ${
          isUser
            ? 'bg-gradient-to-br from-indigo-600 to-purple-600 text-white rounded-br-md'
            : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-700 rounded-bl-md'
        }`}
      >
        <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">{content}</div>

        {isLoading && (
          <div className="flex space-x-1.5 pt-3">
            <motion.div
              className="h-2 w-2 rounded-full bg-current opacity-60"
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 0.6, repeat: Infinity, ease: "easeInOut" }}
            />
            <motion.div
              className="h-2 w-2 rounded-full bg-current opacity-60"
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 0.6, repeat: Infinity, ease: "easeInOut", delay: 0.1 }}
            />
            <motion.div
              className="h-2 w-2 rounded-full bg-current opacity-60"
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 0.6, repeat: Infinity, ease: "easeInOut", delay: 0.2 }}
            />
          </div>
        )}

        <div
          className={`text-[10px] mt-2 font-medium ${
            isUser ? 'text-indigo-100' : 'text-gray-400 dark:text-gray-500'
          }`}
        >
          {format(timestamp, 'HH:mm')}
        </div>
      </div>
    </motion.div>
  );
};
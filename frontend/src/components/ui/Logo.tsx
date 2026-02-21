'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  className?: string;
}

export const Logo: React.FC<LogoProps> = ({
  size = 'md',
  showText = true,
  className = ''
}) => {
  const sizes = {
    sm: { icon: 24, text: 'text-lg' },
    md: { icon: 32, text: 'text-xl' },
    lg: { icon: 40, text: 'text-2xl' }
  };

  const currentSize = sizes[size];

  return (
    <motion.div
      className={`flex items-center gap-2 ${className}`}
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Logo Icon */}
      <motion.div
        whileHover={{ scale: 1.05, rotate: 5 }}
        transition={{ type: "spring", stiffness: 400, damping: 10 }}
      >
        <svg
          width={currentSize.icon}
          height={currentSize.icon}
          viewBox="0 0 40 40"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="drop-shadow-lg"
        >
          {/* Gradient Definitions */}
          <defs>
            <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#6366f1" />
              <stop offset="100%" stopColor="#8b5cf6" />
            </linearGradient>
          </defs>

          {/* Checkmark Circle Background */}
          <circle
            cx="20"
            cy="20"
            r="18"
            fill="url(#logoGradient)"
            className="transition-all duration-300"
          />

          {/* Checkmark */}
          <motion.path
            d="M12 20L17 25L28 14"
            stroke="white"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
          />

          {/* Decorative dots */}
          <circle cx="8" cy="10" r="1.5" fill="#a78bfa" opacity="0.6" />
          <circle cx="32" cy="30" r="1.5" fill="#a78bfa" opacity="0.6" />
        </svg>
      </motion.div>

      {/* Logo Text */}
      {showText && (
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex flex-col leading-none"
        >
          <span className={`font-bold bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent ${currentSize.text}`}>
            TaskFlow
          </span>
          <span className="text-[10px] text-gray-500 dark:text-gray-400 font-medium tracking-wider">
            ORGANIZE • ACHIEVE
          </span>
        </motion.div>
      )}
    </motion.div>
  );
};

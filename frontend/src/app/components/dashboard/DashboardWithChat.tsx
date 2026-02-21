'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import TaskCard from '@/components/dashboard/task-card';
import TaskFormComponent from '@/components/dashboard/task-form';
import { ChatInterface } from '../ChatKit/ChatInterface';
import { FloatingChatBubble } from '@/components/ui/FloatingChatBubble';
import { useAuth } from '@/context/auth-context';
import { Task, TaskForm } from '@/types';
import apiClient from '@/lib/api/client';
import { useRouter } from 'next/navigation';

interface DashboardWithChatProps {
  initialTasks: Task[];
}

export const DashboardWithChat: React.FC<DashboardWithChatProps> = ({ initialTasks }) => {
  const { state, logout } = useAuth();
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [showChat, setShowChat] = useState(false);
  const [showTaskForm, setShowTaskForm] = useState(false);

  const handleTaskUpdate = (updatedTask: Task) => {
    setTasks(prevTasks =>
      prevTasks.map(task => (task.id === updatedTask.id ? updatedTask : task))
    );
  };

  const handleTaskDelete = (taskId: string) => {
    setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
  };

  const handleTaskAdd = (newTask: Task) => {
    setTasks(prevTasks => [...prevTasks, newTask]);
    setShowTaskForm(false);
  };

  const handleTaskFormSubmit = async (data: TaskForm) => {
    try {
      const transformedData = {
        title: data.title,
        description: data.description || '',
        completed: data.status === 'done',
        priority: data.priority || 'medium',
        dueDate: data.dueDate ? new Date(data.dueDate).toISOString() : undefined,
      };

      const response = await apiClient.post<any>('/api/v1/tasks', transformedData);

      if (response.success && response.data) {
        const newTask: Task = {
          ...response.data,
          status: response.data.completed ? 'done' : 'todo',
          createdAt: new Date(response.data.createdAt),
          updatedAt: new Date(response.data.updatedAt || response.data.createdAt),
          priority: response.data.priority || 'medium',
          userId: response.data.userId || state.user?.id || '',
          dueDate: response.data.dueDate ? new Date(response.data.dueDate) : undefined,
        };
        handleTaskAdd(newTask);
      } else {
        console.error('Failed to create task:', response.message || response.error);
        alert('Failed to create task. Please try again.');
      }
    } catch (error: any) {
      console.error('Error creating task:', error);
      alert('An error occurred while creating the task. Please try again.');
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 transition-colors duration-300">
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          {/* Welcome Section */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Welcome back, {state.user?.name || state.user?.email?.split('@')[0]}! 👋
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Here's what you need to focus on today.
            </p>
          </div>

          {/* Tasks Section */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="px-6 py-5 border-b border-gray-200 dark:border-gray-700">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Your Tasks</h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'} total
                  </p>
                </div>
                <motion.button
                  onClick={() => setShowTaskForm(!showTaskForm)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`px-5 py-2.5 rounded-lg font-medium transition-all shadow-lg ${
                    showTaskForm
                      ? 'bg-gray-500 hover:bg-gray-600 text-white'
                      : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white'
                  }`}
                >
                  {showTaskForm ? 'Cancel' : '+ Add Task'}
                </motion.button>
              </div>
            </div>

            <div className="p-6">
              <AnimatePresence>
                {showTaskForm && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                    className="mb-6 p-6 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 rounded-xl border border-gray-200 dark:border-gray-600"
                  >
                    <TaskFormComponent
                      onSubmit={handleTaskFormSubmit}
                      onCancel={() => setShowTaskForm(false)}
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              {tasks.length > 0 ? (
                <div className="space-y-4">
                  {tasks.map((task, index) => (
                    <motion.div
                      key={task.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <TaskCard
                        task={task}
                        onEdit={handleTaskUpdate}
                        onDelete={handleTaskDelete}
                        onStatusChange={(id, status) => {
                          const updatedTask = { ...task, status };
                          handleTaskUpdate(updatedTask);
                        }}
                      />
                    </motion.div>
                  ))}
                </div>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center py-16"
                >
                  <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/30 dark:to-purple-900/30 flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <p className="text-gray-500 dark:text-gray-400 text-lg font-medium">No tasks yet</p>
                  <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">Create your first task to get started!</p>
                </motion.div>
              )}
            </div>
          </div>
        </motion.div>
      </main>

      {/* Floating Chat Bubble */}
      <FloatingChatBubble
        isOpen={showChat}
        onClick={() => setShowChat(!showChat)}
      />

      {/* Chat Panel */}
      <AnimatePresence>
        {showChat && (
          <motion.div
            initial={{ opacity: 0, x: 400 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 400 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed right-6 bottom-24 w-96 h-[600px] z-40 shadow-2xl"
          >
            <ChatInterface />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
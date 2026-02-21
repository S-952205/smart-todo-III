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
    <div className="min-h-screen bg-white dark:bg-gray-900 transition-colors duration-300">
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          {/* Welcome Section */}
          <div className="mb-8">
            <h1 className="text-3xl font-semibold text-[#25343F] dark:text-white mb-2 font-poppins">
              Welcome back, {state.user?.name || state.user?.email?.split('@')[0]}!
            </h1>
            <p className="text-[#25343F]/70 dark:text-gray-400 font-poppins font-light">
              Here's what you need to focus on today.
            </p>
          </div>

          {/* Tasks Section */}
          <div className="bg-white dark:bg-gray-800 rounded-none shadow-sm border border-[#BFC9D1]/40 dark:border-gray-700 overflow-hidden">
            <div className="px-6 py-5 border-b border-[#BFC9D1]/40 dark:border-gray-700">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-semibold text-[#25343F] dark:text-white font-poppins">Your Tasks</h2>
                  <p className="text-sm text-[#25343F]/60 dark:text-gray-400 mt-1 font-poppins font-light">
                    {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'} total
                  </p>
                </div>
                <motion.button
                  onClick={() => setShowTaskForm(!showTaskForm)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`px-5 py-2.5 rounded-none font-medium transition-all font-poppins ${
                    showTaskForm
                      ? 'bg-[#25343F] hover:bg-[#25343F]/90 text-white'
                      : 'bg-[#FF5B5B] hover:bg-[#FF5B5B]/90 text-white'
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
                    className="mb-6 p-6 bg-[#BFC9D1]/10 dark:bg-gray-700 rounded-none border border-[#BFC9D1]/40 dark:border-gray-600"
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
                  <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-[#BFC9D1]/20 dark:bg-gray-700 flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-[#25343F] dark:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <p className="text-[#25343F]/70 dark:text-gray-400 text-lg font-medium font-poppins">No tasks yet</p>
                  <p className="text-[#25343F]/50 dark:text-gray-500 text-sm mt-2 font-poppins font-light">Create your first task to get started!</p>
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
            className="fixed right-4 bottom-20 w-[90vw] sm:w-96 h-[70vh] max-h-[600px] z-40 shadow-2xl"
            style={{ maxHeight: 'calc(100vh - 120px)' }}
          >
            <ChatInterface />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
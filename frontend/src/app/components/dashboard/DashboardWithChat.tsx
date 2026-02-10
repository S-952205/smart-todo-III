'use client';

import React, { useState } from 'react';
import TaskCard from '@/components/dashboard/task-card';
import TaskFormComponent from '@/components/dashboard/task-form';
import { ChatInterface } from '../ChatKit/ChatInterface';
import { useAuth } from '@/context/auth-context';
import { Task, TaskForm } from '@/types'; // Import both Task and TaskForm types
import apiClient from '@/lib/api/client';

interface DashboardWithChatProps {
  initialTasks: Task[];
}

export const DashboardWithChat: React.FC<DashboardWithChatProps> = ({ initialTasks }) => {
  const { state } = useAuth();
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [showChat, setShowChat] = useState(false);

  const handleTaskUpdate = (updatedTask: Task) => {
    setTasks(prevTasks =>
      prevTasks.map(task => (task.id === updatedTask.id ? updatedTask : task))
    );
  };

  const handleTaskDelete = (taskId: string) => {
    setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
  };

  const [showTaskForm, setShowTaskForm] = useState(false);

  const handleTaskAdd = (newTask: Task) => {
    setTasks(prevTasks => [...prevTasks, newTask]);
    setShowTaskForm(false);
  };

  const handleOpenTaskForm = () => {
    setShowTaskForm(true);
  };

  const handleCloseTaskForm = () => {
    setShowTaskForm(false);
  };

  const handleTaskFormSubmit = async (data: TaskForm) => {
    try {
      // Transform form data to match backend API expectations
      const transformedData = {
        title: data.title,
        description: data.description || '',
        completed: data.status === 'done',
        priority: data.priority || 'medium',
        dueDate: data.dueDate ? new Date(data.dueDate).toISOString() : undefined,
      };

      // Call backend API to create task
      const response = await apiClient.post<any>('/api/v1/tasks', transformedData);

      if (response.success && response.data) {
        // Transform backend response to frontend model
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

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                Welcome, {state.user?.name || state.user?.email}
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowChat(!showChat)}
                className={`px-4 py-2 rounded-lg text-white ${
                  showChat ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'
                } transition-colors`}
              >
                {showChat ? 'Hide Chat' : 'Show Chat'}
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Tasks Section */}
          <div className={`${showChat ? 'lg:col-span-2' : 'lg:col-span-3'}`}>
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Your Tasks</h2>
                  {showTaskForm ? (
                    <button
                      onClick={handleCloseTaskForm}
                      className="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors"
                    >
                      Cancel
                    </button>
                  ) : (
                    <button
                      onClick={handleOpenTaskForm}
                      className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                    >
                      Add Task
                    </button>
                  )}
                </div>
                {showTaskForm && (
                  <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <TaskFormComponent onSubmit={handleTaskFormSubmit} onCancel={handleCloseTaskForm} />
                  </div>
                )}

                {tasks.length > 0 ? (
                  <div className="space-y-4">
                    {tasks.map((task) => (
                      <TaskCard
                        key={task.id}
                        task={task}
                        onEdit={handleTaskUpdate} // Pass the updated task to handle any edits
                        onDelete={handleTaskDelete}
                        onStatusChange={(id, status) => {
                          // Update the task status
                          const updatedTask = { ...task, status };
                          handleTaskUpdate(updatedTask);
                        }}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500 dark:text-gray-400">No tasks yet. Add your first task!</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Chat Section - Only show if chat is enabled */}
          {showChat && (
            <div className="lg:col-span-1">
              <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg h-full">
                <div className="px-4 py-5 sm:p-6 h-full flex flex-col">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">AI Assistant</h2>
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <ChatInterface />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
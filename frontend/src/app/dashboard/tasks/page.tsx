'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Task } from '@/types';
import TaskCard from '@/components/dashboard/task-card';
import TaskForm from '@/components/dashboard/task-form';
import apiClient from '@/lib/api/client';
import { useAuth } from '@/context/auth-context';
import { ChatInterface } from '@/app/components/ChatKit/ChatInterface';
import { FloatingChatBubble } from '@/components/ui/FloatingChatBubble';

const TasksPage: React.FC = () => {
  const { state } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState<boolean>(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [filter, setFilter] = useState<'all' | 'todo' | 'in-progress' | 'done'>('all');
  const [showChat, setShowChat] = useState(false);

  // Fetch tasks from API
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        setError(null); // Clear any previous errors
        const response = await apiClient.get<any[]>('/api/v1/tasks');

        if (response.success) {
          // Transform dates to Date objects
          const transformedTasks = response.data ? response.data.map(task => ({
            ...task,
            createdAt: new Date(task.created_at),
            updatedAt: new Date(task.updated_at),
            dueDate: task.due_date ? new Date(task.due_date) : undefined,
            userId: task.user_id
          })) : [];
          setTasks(transformedTasks);
        } else {
          // Only set error if it's a real failure, not just empty data
          if (response.error && response.error !== 'No tasks found') {
            setError(response.message || response.error || 'Failed to fetch tasks');
          } else {
            setTasks([]); // Empty tasks, not an error
          }
        }
      } catch (err: any) {
        // Only show error for actual network/server errors
        setError(err.message || 'Unable to connect to server. Please try again.');
        console.error('Error fetching tasks:', err);
      } finally {
        setLoading(false);
      }
    };

    if (state.isAuthenticated) {
      fetchTasks();
    }
  }, [state.isAuthenticated]);

  // Handle form submission (create/update)
  const handleFormSubmit = async (formData: any) => {
    try {
      // Convert frontend camelCase to backend snake_case
      const backendData = {
        title: formData.title,
        description: formData.description,
        status: formData.status,
        priority: formData.priority,
        due_date: formData.dueDate ? formData.dueDate.toISOString() : null
      };

      if (editingTask) {
        // Update existing task
        const response = await apiClient.put<any>(`/api/v1/tasks/${editingTask.id}`, backendData);

        if (response.success) {
          // Transform response to frontend model
          const updatedTask = {
            ...response.data,
            createdAt: new Date(response.data.created_at),
            updatedAt: new Date(response.data.updated_at),
            dueDate: response.data.due_date ? new Date(response.data.due_date) : undefined,
            userId: response.data.user_id
          };
          setTasks(tasks.map(task =>
            task.id === editingTask.id ? updatedTask : task
          ));
          setEditingTask(null);
          setShowForm(false);
        } else {
          setError(response.message || response.error || 'Failed to update task');
        }
      } else {
        // Create new task
        const response = await apiClient.post<any>('/api/v1/tasks', backendData);

        if (response.success) {
          // Transform response to frontend model
          const newTask = {
            ...response.data,
            createdAt: new Date(response.data.created_at),
            updatedAt: new Date(response.data.updated_at),
            dueDate: response.data.due_date ? new Date(response.data.due_date) : undefined,
            userId: response.data.user_id
          };
          setTasks([...tasks, newTask]);
          setShowForm(false);
        } else {
          setError(response.message || response.error || 'Failed to create task');
        }
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while saving the task');
      console.error('Error saving task:', err);
    }
  };

  // Handle task deletion
  const handleDeleteTask = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        const response = await apiClient.delete(`/api/v1/tasks/${id}`);

        if (response.success) {
          setTasks(tasks.filter(task => task.id !== id));
        } else {
          setError(response.message || response.error || 'Failed to delete task');
        }
      } catch (err: any) {
        setError(err.message || 'An error occurred while deleting the task');
        console.error('Error deleting task:', err);
      }
    }
  };

  // Handle task status change
  const handleStatusChange = async (id: string, status: 'todo' | 'in-progress' | 'done') => {
    try {
      const taskToUpdate = tasks.find(task => task.id === id);
      if (!taskToUpdate) return;

      // Send status update to backend
      const backendData = {
        status
      };

      const response = await apiClient.put<any>(`/api/v1/tasks/${id}`, backendData);

      if (response.success) {
        // Transform response to frontend model
        const updatedTask = {
          ...response.data,
          createdAt: new Date(response.data.created_at),
          updatedAt: new Date(response.data.updated_at),
          dueDate: response.data.due_date ? new Date(response.data.due_date) : undefined,
          userId: response.data.user_id
        };
        setTasks(tasks.map(task =>
          task.id === id ? updatedTask : task
        ));
      } else {
        setError(response.message || response.error || 'Failed to update task status');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while updating task status');
      console.error('Error updating task status:', err);
    }
  };

  // Filter tasks based on selected filter
  const filteredTasks = tasks.filter(task => {
    if (filter === 'all') return true;
    return task.status === filter;
  });

  // Loading state
  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-8">
          <div className="flex justify-center items-center min-h-[400px]">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#FF5B5B]"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-semibold text-[#25343F] font-poppins">My Tasks</h1>

          <div className="flex space-x-4">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as any)}
              className="border border-[#BFC9D1]/40 rounded-none px-3 py-2 bg-white text-[#25343F] focus:outline-none focus:ring-2 focus:ring-[#FF5B5B] font-poppins"
            >
              <option value="all">All Tasks</option>
              <option value="todo">To Do</option>
              <option value="in-progress">In Progress</option>
              <option value="done">Completed</option>
            </select>

            <button
              onClick={() => {
                setEditingTask(null);
                setShowForm(true);
              }}
              className="bg-[#FF5B5B] hover:bg-[#FF5B5B]/90 text-white px-4 py-2 rounded-none font-medium transition-all font-poppins"
            >
              Add New Task
            </button>
          </div>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-4 bg-[#FF5B5B]/10 border-l-4 border-[#FF5B5B] text-[#25343F] px-4 py-3 rounded-none"
          >
            <p className="font-poppins">{error}</p>
          </motion.div>
        )}

        {showForm ? (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-white border border-[#BFC9D1]/40 p-6 rounded-none shadow-sm mb-6"
          >
            <h2 className="text-lg font-semibold text-[#25343F] mb-4 font-poppins">
              {editingTask ? 'Edit Task' : 'Create New Task'}
            </h2>
            <TaskForm
              task={editingTask || undefined}
              onSubmit={handleFormSubmit}
              onCancel={() => {
                setShowForm(false);
                setEditingTask(null);
              }}
              submitText={editingTask ? 'Update Task' : 'Create Task'}
            />
          </motion.div>
        ) : null}

        {filteredTasks.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-16"
          >
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-[#BFC9D1]/20 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-[#25343F]/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-[#25343F] mb-2 font-poppins">
              {tasks.length === 0 ? 'No tasks yet' : 'No tasks match your filter'}
            </h3>
            <p className="text-[#25343F]/60 mb-6 font-poppins font-light">
              {tasks.length === 0
                ? 'Start organizing your work by creating your first task'
                : 'Try selecting a different filter to see your tasks'}
            </p>
            {tasks.length === 0 && (
              <button
                onClick={() => {
                  setEditingTask(null);
                  setShowForm(true);
                }}
                className="bg-[#FF5B5B] hover:bg-[#FF5B5B]/90 text-white px-6 py-3 rounded-none font-medium transition-all font-poppins"
              >
                Create Your First Task
              </button>
            )}
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onEdit={(task) => {
                  setEditingTask(task);
                  setShowForm(true);
                }}
                onDelete={handleDeleteTask}
                onStatusChange={handleStatusChange}
              />
            ))}
          </div>
        )}
      </div>

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

export default TasksPage;
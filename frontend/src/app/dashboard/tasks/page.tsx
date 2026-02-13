'use client';

import React, { useState, useEffect } from 'react';
import { Task } from '@/types';
import TaskCard from '@/components/dashboard/task-card';
import TaskForm from '@/components/dashboard/task-form';
import apiClient from '@/lib/api/client';
import { useAuth } from '@/context/auth-context';
import Link from 'next/link';

const TasksPage: React.FC = () => {
  const { state } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState<boolean>(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [filter, setFilter] = useState<'all' | 'todo' | 'in-progress' | 'done'>('all');

  // Fetch tasks from API
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get<any[]>('/api/v1/tasks');

        if (response.success && response.data) {
          // Transform dates to Date objects
          const transformedTasks = response.data.map(task => ({
            ...task,
            createdAt: new Date(task.created_at),
            updatedAt: new Date(task.updated_at),
            dueDate: task.due_date ? new Date(task.due_date) : undefined,
            userId: task.user_id
          }));
          setTasks(transformedTasks);
        } else {
          setError(response.message || response.error || 'Failed to fetch tasks');
        }
      } catch (err: any) {
        setError(err.message || 'An error occurred while fetching tasks');
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
          <div className="flex justify-center items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>

          <div className="flex space-x-4">
            <Link href="/dashboard" className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700">
              Chat with AI Assistant
            </Link>

            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as any)}
              className="border rounded-md px-3 py-2"
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
              className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
            >
              Add New Task
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {showForm ? (
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
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
          </div>
        ) : null}

        {filteredTasks.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No tasks found. {tasks.length === 0 ? 'Create your first task!' : 'Try changing your filter.'}</p>
          </div>
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
    </div>
  );
};

export default TasksPage;
import React from 'react';
import { Task } from '@/types';

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (id: string) => void;
  onStatusChange: (id: string, status: 'todo' | 'in-progress' | 'done') => void;
}

const TaskCard: React.FC<TaskCardProps> = ({ task, onEdit, onDelete, onStatusChange }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'todo':
        return 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/30 dark:text-blue-200 dark:border-blue-700';
      case 'in-progress':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-200 dark:border-yellow-700';
      case 'done':
        return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-200 dark:border-green-700';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600';
    }
  };

  const getPriorityColor = (priority?: string) => {
    if (!priority) return '';
    switch (priority.toLowerCase()) {
      case 'high':
        return 'border-l-4 border-l-red-500';
      case 'medium':
        return 'border-l-4 border-l-yellow-500';
      case 'low':
        return 'border-l-4 border-l-green-500';
      default:
        return '';
    }
  };

  return (
    <div className={` border-red-400 p-5 shadow-md bg-white dark:bg-gray-800 dark:border-gray-700 transition-all duration-200 hover:shadow-md ${getPriorityColor(task.priority)}`}>
      <div className="flex justify-between items-start">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-lg text-gray-900 dark:text-white break-words">{task.title}</h3>
          {task.description && (
            <p className="text-gray-600 dark:text-gray-300 mt-2 text-sm break-words leading-relaxed">{task.description}</p>
          )}
        </div>
        <div className="flex space-x-2 ml-3 flex-shrink-0">
          <button
            onClick={() => onEdit(task)}
            className="text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300 p-1 rounded-md hover:bg-indigo-50 dark:hover:bg-gray-700 transition-colors"
            aria-label="Edit task"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
            </svg>
          </button>
          <button
            onClick={() => onDelete(task.id)}
            className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 p-1 rounded-md hover:bg-red-50 dark:hover:bg-gray-700 transition-colors"
            aria-label="Delete task"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-2">
        <span className={`px-3 py-1 text-xs font-medium rounded-full border ${getStatusColor(task.status)}`}>
          {task.status.replace('-', ' ')}
        </span>

        <select
          value={task.status}
          onChange={(e) => onStatusChange(task.id, e.target.value as 'todo' | 'in-progress' | 'done')}
          className="text-xs border border-gray-300 dark:border-gray-600 rounded-lg px-2 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          <option value="todo">To Do</option>
          <option value="in-progress">In Progress</option>
          <option value="done">Done</option>
        </select>
      </div>

      {(task.dueDate || task.priority) && (
        <div className="mt-3 flex flex-wrap gap-3 text-xs text-gray-500 dark:text-gray-400">
          {task.dueDate && (
            <div className="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Due: {new Date(task.dueDate).toLocaleDateString()}
            </div>
          )}
          {task.priority && (
            <div className="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 11l7-7 7 7M5 19l7-7 7 7" />
              </svg>
              Priority: {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
            </div>
          )}
        </div>
      )}

      <div className="mt-3 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        <div className="flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Created: {new Date(task.createdAt).toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

export default TaskCard;
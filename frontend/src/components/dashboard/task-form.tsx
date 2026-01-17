import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { TaskFormSchema } from '@/types/validation';
import { TaskForm } from '@/types';

interface TaskFormComponentProps {
  task?: TaskForm;
  onSubmit: (data: TaskForm) => void;
  onCancel: () => void;
  submitText?: string;
}

const TaskFormComponent: React.FC<TaskFormComponentProps> = ({
  task,
  onSubmit,
  onCancel,
  submitText = 'Save Task'
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue
  } = useForm<TaskForm>({
    resolver: zodResolver(TaskFormSchema),
    defaultValues: task || {
      title: '',
      description: '',
      status: 'todo',
      dueDate: undefined,
      priority: 'medium'
    }
  });

  // Set default values if task prop changes
  React.useEffect(() => {
    if (task) {
      setValue('title', task.title || '');
      setValue('description', task.description || '');
      setValue('status', task.status || 'todo');
      setValue('dueDate', task.dueDate ? new Date(task.dueDate).toISOString().split('T')[0] : undefined);
      setValue('priority', task.priority || 'medium');
    }
  }, [task, setValue]);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Title *
        </label>
        <input
          id="title"
          {...register('title')}
          type="text"
          className={`mt-1 block w-full px-4 py-3 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-700 dark:border-gray-600 dark:text-white ${
            errors.title ? 'border-red-500 dark:border-red-400' : 'border-gray-300 dark:border-gray-600'
          }`}
          placeholder="Enter task title..."
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.title.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Description
        </label>
        <textarea
          id="description"
          {...register('description')}
          rows={4}
          className="mt-1 block w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-700 dark:text-white"
          placeholder="Enter task description..."
        ></textarea>
        {errors.description && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.description.message}</p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Status
          </label>
          <select
            id="status"
            {...register('status')}
            className="mt-1 block w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-700 dark:text-white"
          >
            <option value="todo">To Do</option>
            <option value="in-progress">In Progress</option>
            <option value="done">Done</option>
          </select>
          {errors.status && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.status.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Priority
          </label>
          <select
            id="priority"
            {...register('priority')}
            className="mt-1 block w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-700 dark:text-white"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div>
          <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Due Date
          </label>
          <input
            id="dueDate"
            {...register('dueDate')}
            type="date"
            className="mt-1 block w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-700 dark:text-white"
          />
          {errors.dueDate && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.dueDate.message as string}</p>
          )}
        </div>
      </div>

      <div className="flex space-x-3 pt-2">
        <button
          type="submit"
          className="inline-flex justify-center py-3 px-6 border border-transparent shadow-sm text-base font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
        >
          {submitText}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="inline-flex justify-center py-3 px-6 border border-gray-300 shadow-sm text-base font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 dark:bg-gray-700 dark:text-white dark:border-gray-600 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

export default TaskFormComponent;
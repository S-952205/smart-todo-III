import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion } from 'framer-motion';
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
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      {/* Title Field */}
      <div>
        <label htmlFor="title" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          Title <span className="text-red-500">*</span>
        </label>
        <input
          id="title"
          {...register('title')}
          type="text"
          className={`w-full px-4 py-3 border rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-white dark:bg-gray-800 dark:text-white ${
            errors.title ? 'border-red-500 dark:border-red-400' : 'border-gray-300 dark:border-gray-600'
          }`}
          placeholder="Enter task title..."
        />
        {errors.title && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-2 text-sm text-red-600 dark:text-red-400"
          >
            {errors.title.message}
          </motion.p>
        )}
      </div>

      {/* Description Field */}
      <div>
        <label htmlFor="description" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          Description
        </label>
        <textarea
          id="description"
          {...register('description')}
          rows={4}
          className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-white dark:bg-gray-800 dark:text-white resize-none"
          placeholder="Enter task description..."
        ></textarea>
        {errors.description && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-2 text-sm text-red-600 dark:text-red-400"
          >
            {errors.description.message}
          </motion.p>
        )}
      </div>

      {/* Status, Priority, Due Date Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Status Field */}
        <div>
          <label htmlFor="status" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            Status
          </label>
          <select
            id="status"
            {...register('status')}
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-white dark:bg-gray-800 dark:text-white cursor-pointer"
          >
            <option value="todo">To Do</option>
            <option value="in-progress">In Progress</option>
            <option value="done">Done</option>
          </select>
          {errors.status && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-2 text-sm text-red-600 dark:text-red-400"
            >
              {errors.status.message}
            </motion.p>
          )}
        </div>

        {/* Priority Field */}
        <div>
          <label htmlFor="priority" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            Priority
          </label>
          <select
            id="priority"
            {...register('priority')}
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-white dark:bg-gray-800 dark:text-white cursor-pointer"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        {/* Due Date Field */}
        <div>
          <label htmlFor="dueDate" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            Due Date
          </label>
          <input
            id="dueDate"
            {...register('dueDate')}
            type="date"
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-white dark:bg-gray-800 dark:text-white"
          />
          {errors.dueDate && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-2 text-sm text-red-600 dark:text-red-400"
            >
              {errors.dueDate.message as string}
            </motion.p>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 pt-2">
        <motion.button
          type="submit"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex-1 py-3 px-6 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition-all"
        >
          {submitText}
        </motion.button>
        <motion.button
          type="button"
          onClick={onCancel}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex-1 py-3 px-6 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold rounded-xl bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition-all"
        >
          Cancel
        </motion.button>
      </div>
    </form>
  );
};

export default TaskFormComponent;
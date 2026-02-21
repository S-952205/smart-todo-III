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
        <label htmlFor="title" className="block text-sm font-medium text-[#25343F] dark:text-gray-300 mb-2 font-poppins">
          Title <span className="text-[#FF5B5B]">*</span>
        </label>
        <input
          id="title"
          {...register('title')}
          type="text"
          className={`w-full px-4 py-3 border rounded-none shadow-sm focus:outline-none focus:ring-2 focus:ring-[#FF5B5B] focus:border-[#FF5B5B] transition-all bg-white dark:bg-gray-800 dark:text-white font-poppins ${
            errors.title ? 'border-[#FF5B5B] dark:border-[#FF5B5B]' : 'border-[#BFC9D1]/40 dark:border-gray-600'
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
        <label htmlFor="description" className="block text-sm font-medium text-[#25343F] dark:text-gray-300 mb-2 font-poppins">
          Description
        </label>
        <textarea
          id="description"
          {...register('description')}
          rows={4}
          className="w-full px-4 py-3 border border-[#BFC9D1]/40 dark:border-gray-600 rounded-none shadow-sm focus:outline-none focus:ring-2 focus:ring-[#FF5B5B] focus:border-[#FF5B5B] transition-all bg-white dark:bg-gray-800 dark:text-white resize-none font-poppins"
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
          <label htmlFor="status" className="block text-sm font-medium text-[#25343F] dark:text-gray-300 mb-2 font-poppins">
            Status
          </label>
          <select
            id="status"
            {...register('status')}
            className="w-full px-4 py-3 border border-[#BFC9D1]/40 dark:border-gray-600 rounded-none shadow-sm focus:outline-none focus:ring-2 focus:ring-[#FF5B5B] focus:border-[#FF5B5B] transition-all bg-white dark:bg-gray-800 dark:text-white cursor-pointer font-poppins"
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
          <label htmlFor="priority" className="block text-sm font-medium text-[#25343F] dark:text-gray-300 mb-2 font-poppins">
            Priority
          </label>
          <select
            id="priority"
            {...register('priority')}
            className="w-full px-4 py-3 border border-[#BFC9D1]/40 dark:border-gray-600 rounded-none shadow-sm focus:outline-none focus:ring-2 focus:ring-[#FF5B5B] focus:border-[#FF5B5B] transition-all bg-white dark:bg-gray-800 dark:text-white cursor-pointer font-poppins"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        {/* Due Date Field */}
        <div>
          <label htmlFor="dueDate" className="block text-sm font-medium text-[#25343F] dark:text-gray-300 mb-2 font-poppins">
            Due Date
          </label>
          <input
            id="dueDate"
            {...register('dueDate')}
            type="date"
            className="w-full px-4 py-3 border border-[#BFC9D1]/40 dark:border-gray-600 rounded-none shadow-sm focus:outline-none focus:ring-2 focus:ring-[#FF5B5B] focus:border-[#FF5B5B] transition-all bg-white dark:bg-gray-800 dark:text-white font-poppins"
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
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          className="flex-1 py-3 px-6 bg-[#FF5B5B] hover:bg-[#FF5B5B]/90 text-white font-medium rounded-none shadow-sm hover:shadow-md focus:outline-none focus:ring-2 focus:ring-[#FF5B5B] focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition-all font-poppins"
        >
          {submitText}
        </motion.button>
        <motion.button
          type="button"
          onClick={onCancel}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          className="flex-1 py-3 px-6 border-2 border-[#BFC9D1]/40 dark:border-gray-600 text-[#25343F] dark:text-gray-300 font-medium rounded-none bg-white dark:bg-gray-800 hover:bg-[#BFC9D1]/10 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-[#25343F] focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition-all font-poppins"
        >
          Cancel
        </motion.button>
      </div>
    </form>
  );
};

export default TaskFormComponent;
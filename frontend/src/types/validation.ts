import { z } from 'zod';

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const LoginFormSchema = z.object({
  email: z.string().regex(emailRegex, 'Invalid email format'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

const SignupFormSchema = LoginFormSchema.extend({
  name: z.string().min(1, 'Name is required').max(100),
});

const TaskFormSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().max(1000).optional(),
  status: z.enum(['todo', 'in-progress', 'done']),
  dueDate: z.coerce.date().optional(),
  priority: z.enum(['low', 'medium', 'high']).optional(),
});

// Export all schemas
export {
  LoginFormSchema,
  SignupFormSchema,
  TaskFormSchema
};
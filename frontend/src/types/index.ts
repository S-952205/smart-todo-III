// User Session Model
export interface UserSession {
  id: string;           // Unique identifier for the user session
  userId: string;       // Reference to the user ID from authentication
  email: string;        // User's email address
  name?: string;        // Optional user name
  accessToken: string;  // JWT access token
  refreshToken?: string; // Optional refresh token
  expiresAt: Date;      // Token expiration time
  createdAt: Date;      // Session creation time
  updatedAt: Date;      // Last session update time
}

// Authentication State Model
export interface AuthState {
  isAuthenticated: boolean;
  user: UserSession | null;
  isLoading: boolean;
  error: string | null;
}

// API Response Models
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    pageSize: number;
    totalCount: number;
    totalPages: number;
  };
}

// Task Model (Frontend Representation)
export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'todo' | 'in-progress' | 'done';
  userId: string;       // Owner of the task
  createdAt: Date;
  updatedAt: Date;
  dueDate?: Date;
  priority?: 'low' | 'medium' | 'high';
}

// Form Data Models
export interface LoginForm {
  email: string;
  password: string;
}

export interface SignupForm extends LoginForm {
  name: string;
}

export interface TaskForm {
  title: string;
  description?: string;
  status: 'todo' | 'in-progress' | 'done';
  dueDate?: any;
  priority?: 'low' | 'medium' | 'high';
}

// State Management Models
export interface TaskState {
  tasks: Task[];
  filteredTasks: Task[];
  loading: boolean;
  error: string | null;
  selectedTask: Task | null;
  filters: {
    status?: 'todo' | 'in-progress' | 'done';
    searchTerm?: string;
  };
}

// API Client Configuration Model
export interface ApiClientConfig {
  baseUrl: string;
  defaultHeaders: Record<string, string>;
  timeout: number;
  retries: number;
}

// Security Models
export interface SecureToken {
  value: string;
  type: 'access' | 'refresh';
  expiresAt: Date;
  isValid(): boolean;
  isExpired(): boolean;
  willExpireSoon(minutes?: number): boolean;
}
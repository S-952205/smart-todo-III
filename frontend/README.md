# Frontend Authentication & AI Chatbot System

This is the frontend application for the Todo Full Stack application, built with Next.js 16+, React 18, TypeScript, and Tailwind CSS. It implements a complete authentication system with user registration, login, protected dashboard access, and an AI-powered chatbot for natural language task management.

## Features

- User registration and login with Better Auth
- Protected routes with authentication
- Task management system with CRUD operations
- **AI Chatbot Interface**: Natural language task management via ChatKit UI
- **Conversation History**: Persistent chat sessions with message history
- **MCP Tools Integration**: AI agent can perform task operations through chat
- Responsive design with Tailwind CSS
- JWT-based authentication
- Form validation with Zod and React Hook Form
- API client with automatic token refresh

## Tech Stack

- Next.js 16+ with App Router
- React 18
- TypeScript 5+
- Tailwind CSS
- Better Auth
- Zod for validation
- React Hook Form
- Shadcn UI components
- ChatKit UI for AI chatbot interface

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── (auth)/          # Authentication pages (login, signup)
│   │   │   ├── login/
│   │   │   └── signup/
│   │   ├── api/
│   │   │   └── chat/
│   │   │       └── chatService.ts    # Chat API service
│   │   ├── dashboard/       # Protected dashboard route
│   │   │   └── page.tsx     # Main dashboard with integrated chat
│   │   ├── globals.css      # Global styles
│   │   └── layout.tsx       # Root layout
│   ├── components/          # Reusable UI components
│   │   ├── ui/              # Base UI components (Shadcn)
│   │   ├── auth/            # Authentication-related components
│   │   ├── dashboard/       # Dashboard components
│   │   │   ├── DashboardWithChat.tsx  # Dashboard with AI chat integration
│   │   │   ├── task-card.tsx          # Task display component
│   │   │   └── task-form.tsx          # Task creation/edit form
│   │   ├── ChatKit/         # AI Chatbot UI components
│   │   │   ├── ChatInterface.tsx      # Main chat interface
│   │   │   ├── Message.tsx            # Message display component
│   │   │   └── MessageInput.tsx       # Message input component
│   │   └── navbar/          # Navigation bar component
│   ├── context/             # React context providers
│   │   └── auth-context.tsx # Authentication context
│   ├── lib/                 # Utility functions and services
│   │   ├── auth/            # Authentication utilities
│   │   ├── api/             # API client with JWT handling
│   │   │   └── client.ts    # API client with automatic token refresh
│   │   └── utils/           # General utilities
│   └── types/               # TypeScript type definitions
│       ├── index.ts         # Task and general types
│       └── chat.ts          # Chat-related types
├── public/                  # Static assets
├── .env.local               # Environment variables (JWT secret, API URLs)
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json            # TypeScript configuration
```

## API Client Usage

The application uses a custom API client located at `src/lib/api/client.ts` that handles JWT authentication and token refresh automatically.

### Task Management Examples:

```typescript
import apiClient from '@/lib/api/client';

// GET request - List tasks
const response = await apiClient.get('/api/v1/tasks');

// POST request - Create task
const response = await apiClient.post('/api/v1/tasks', {
  title: 'New Task',
  description: 'Task description',
  status: 'todo',
  priority: 'medium'
});

// PUT request - Update task
const response = await apiClient.put(`/api/v1/tasks/${taskId}`, {
  title: 'Updated Task',
  status: 'in-progress',
  priority: 'high'
});

// DELETE request - Delete task
const response = await apiClient.delete(`/api/v1/tasks/${taskId}`);
```

### AI Chat Examples:

```typescript
import apiClient from '@/lib/api/client';

// POST request - Send chat message
const response = await apiClient.post('/api/v1/chat', {
  message: 'Add a task to buy groceries',
  conversation_id: conversationId // Optional, for continuing existing conversation
});

// GET request - List conversations
const response = await apiClient.get('/api/v1/chat/conversations');

// GET request - Get conversation with messages
const response = await apiClient.get(`/api/v1/chat/conversations/${conversationId}`);

// DELETE request - Delete conversation
const response = await apiClient.delete(`/api/v1/chat/conversations/${conversationId}`);
```

The API client automatically:
- Adds the Authorization header with the JWT token
- Handles token refresh when receiving a 401 response
- Redirects to login if token refresh fails
- Returns standardized response objects

## Environment Variables

Copy `.env.local.example` to `.env.local` and update the values:

```env
# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BASE_URL=http://localhost:3000

# Better Auth Configuration
AUTH_SECRET=your_auth_secret_here
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_URL=http://localhost:3000

# Database Configuration (if needed for Better Auth)
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db

# JWT Configuration
JWT_SECRET=your_jwt_secret_here
JWT_EXPIRES_IN=24h
```

**Note**: The `NEXT_PUBLIC_API_URL` should point to your backend API server. All chat and task operations are routed through this API endpoint.

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Visit `http://localhost:3000` in your browser.

## Authentication Flow

1. Users can register at `/signup` or login at `/login`
2. Successful authentication stores session data in localStorage
3. Protected routes are wrapped with `ProtectedRoute` component
4. API requests automatically include the JWT token in the Authorization header
5. Token refresh happens automatically when receiving a 401 response
6. All chat and task operations require valid authentication

## AI Chatbot Features

### Natural Language Task Management

The AI chatbot allows users to manage tasks through natural conversation:

- **Create tasks**: "Add a task to buy groceries"
- **List tasks**: "Show me my tasks" or "What do I need to do?"
- **Update tasks**: "Set my grocery task to high priority" or "Mark meeting prep as in progress"
- **Complete tasks**: "Complete my grocery shopping task"
- **Delete tasks**: "Delete the meeting task"

### Conversation History

- All chat conversations are persisted in the database
- Users can view previous conversations and their message history
- Each conversation maintains context for better AI responses
- Conversations can be deleted when no longer needed

### MCP Tools Integration

The AI agent uses MCP (Model Context Protocol) tools to perform task operations:
- All operations enforce JWT authentication
- User isolation is maintained (users can only access their own tasks)
- Tool calls are transparent to the user
- Error handling provides clear feedback when operations fail

## Components

### Authentication Components
- `AuthProvider` and `useAuth` hook: Manages authentication state
- `ProtectedRoute`: Wraps protected pages/components

### Task Management Components
- `TaskCard`: Displays individual tasks with status, priority, and actions
- `TaskForm`: Handles task creation and editing with validation
- `DashboardWithChat`: Main dashboard integrating tasks and AI chat

### AI Chatbot Components (ChatKit)
- `ChatInterface`: Main chat interface with message history and input
- `Message`: Displays individual chat messages (user and assistant)
- `MessageInput`: Text input component for sending messages to AI

### Navigation Components
- `Navbar`: Navigation bar with user profile and logout

## Usage

### Starting the Application

1. Make sure the backend API is running on `http://localhost:8000`
2. Start the frontend development server:
```bash
npm run dev
```
3. Visit `http://localhost:3000` in your browser
4. Register a new account or login with existing credentials
5. Access the dashboard to manage tasks and chat with the AI assistant

### Using the AI Chatbot

1. Click the "Show Chat" button on the dashboard to open the AI assistant
2. Type natural language commands like:
   - "Add a task to prepare presentation"
   - "Show me all my tasks"
   - "Set the presentation task to high priority"
   - "Mark the grocery task as done"
3. The AI will process your request and perform the appropriate task operations
4. All conversations are saved and can be accessed later

### Task Management

You can manage tasks through:
- **Traditional UI**: Use the "Add Task" button and task cards for direct manipulation
- **AI Chat**: Use natural language to create, update, complete, or delete tasks
- Both methods work seamlessly together and keep data synchronized

## Development

### Build for Production

```bash
npm run build
```

### Run Production Build

```bash
npm start
```

### Linting

```bash
npm run lint
```

## Architecture Notes

- The application uses Next.js App Router for routing and server components
- Authentication state is managed via React Context
- API calls are centralized through the `apiClient` utility
- Chat interface maintains local state for real-time updates
- All data persistence happens through the backend API
- JWT tokens are stored in localStorage and automatically included in API requests

## Troubleshooting

### Chat not working
- Verify backend is running and `NEXT_PUBLIC_API_URL` is correct
- Check that OpenRouter API key is configured in backend `.env`
- Ensure JWT token is valid (try logging out and back in)

### Tasks not syncing
- Check browser console for API errors
- Verify backend database connection is working
- Ensure user_id in JWT matches the authenticated user

### Authentication issues
- Clear localStorage and try logging in again
- Verify `AUTH_SECRET` matches between frontend and backend
- Check that Better Auth is properly configured

# Authentication Utilities for Chat Service

## Overview
This document describes how the authentication utilities work with the chat service to ensure secure communication between the frontend and backend.

## Files
- `frontend/src/lib/auth.ts`: Main authentication utility functions
- `frontend/src/app/api/chat/chatService.ts`: Chat service that uses the auth utilities

## Key Functions

### getToken()
Retrieves the user's access token from various storage locations:
1. First tries localStorage ('userSession' key) - matches AuthContext implementation
2. Falls back to sessionStorage ('accessToken' key)
3. Finally tries cookies (__Secure-authjs.session-token and authjs.csrf-token)

### isAuthenticated()
Checks if the user has a valid session by verifying token existence and validity.

### isTokenValid()
Verifies that the stored token hasn't expired.

### refreshAccessToken()
Automatically refreshes the access token when it's close to expiring (within 5 minutes).

### storeSession() / removeSession()
Helper functions to manage user session storage.

## Integration with Chat Service

The chat service imports and uses `getToken()` to authenticate API requests:

```typescript
async sendMessage(message: string, conversationId?: string): Promise<ChatResponse> {
  try {
    const token = getToken(); // Gets the current user's token

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`; // Adds token to request
    }

    // Makes authenticated request to backend
    const response = await fetch(`${this.baseUrl}/v1/chat`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });

    // Handles 401 Unauthorized responses appropriately
    if (response.status === 401) {
      localStorage.removeItem('userSession');
      window.location.href = '/login';
      throw new Error('Authentication required. Please log in.');
    }

    return response.json();
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
}
```

## Error Handling
- All chat service methods check for 401 responses and redirect to login
- Invalid/expired tokens are automatically removed from storage
- Proper error logging is implemented throughout

## Security Features
- Tokens are validated for expiration before use
- Automatic token refresh when approaching expiration
- Secure storage in localStorage with proper cleanup
- Authorization headers added to all authenticated requests

## Compatibility
- Works with the existing AuthContext implementation
- Compatible with Better Auth cookie-based storage
- Follows industry-standard JWT authentication patterns
/**
 * Authentication Utilities for Frontend
 * Provides functions to handle authentication tokens and user sessions
 */

/**
 * Get the current user's access token from storage
 * @returns The access token string or null if not authenticated
 */
export const getToken = (): string | null => {
  try {
    // First try to get from localStorage (where our AuthContext stores it)
    const storedSession = localStorage.getItem('userSession');
    if (storedSession) {
      const session = JSON.parse(storedSession);
      if (session.accessToken) {
        // Check if token is still valid (not expired)
        const expiresAt = new Date(session.expiresAt);
        if (expiresAt > new Date()) {
          return session.accessToken;
        } else {
          // Token is expired, remove the session
          localStorage.removeItem('userSession');
          return null;
        }
      }
    }

    // Fallback: try to get from sessionStorage
    const storedToken = sessionStorage.getItem('accessToken');
    if (storedToken) {
      return storedToken;
    }

    // Fallback: try to get from cookies (Better Auth typically stores tokens in cookies)
    const cookieToken = getCookie('__Secure-authjs.session-token');
    if (cookieToken) {
      return cookieToken;
    }

    // Another common Better Auth cookie name
    const csrfToken = getCookie('authjs.csrf-token');
    if (csrfToken) {
      // Extract the actual token from the CSRF token cookie value
      const token = csrfToken.split('|')[0];
      return token;
    }

    return null;
  } catch (error) {
    console.error('Error retrieving token:', error);
    return null;
  }
};

/**
 * Get a cookie value by name
 * @param name The name of the cookie
 * @returns The cookie value or null if not found
 */
const getCookie = (name: string): string | null => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
};

/**
 * Store the user session in localStorage
 * @param session The user session object to store
 */
export const storeSession = (session: any): void => {
  try {
    localStorage.setItem('userSession', JSON.stringify(session));
  } catch (error) {
    console.error('Error storing session:', error);
  }
};

/**
 * Remove the stored user session
 */
export const removeSession = (): void => {
  try {
    localStorage.removeItem('userSession');
    sessionStorage.removeItem('accessToken');
  } catch (error) {
    console.error('Error removing session:', error);
  }
};

/**
 * Check if the user is currently authenticated
 * @returns Boolean indicating authentication status
 */
export const isAuthenticated = (): boolean => {
  const token = getToken();
  return token !== null && token.length > 0;
};

/**
 * Validate if the current token is still valid
 * @returns Boolean indicating if token is valid
 */
export const isTokenValid = (): boolean => {
  try {
    const storedSession = localStorage.getItem('userSession');
    if (storedSession) {
      const session = JSON.parse(storedSession);
      const expiresAt = new Date(session.expiresAt);
      return expiresAt > new Date();
    }
    return false;
  } catch (error) {
    console.error('Error validating token:', error);
    return false;
  }
};

/**
 * Refresh the access token if it's about to expire
 * @returns Boolean indicating if refresh was successful
 */
export const refreshAccessToken = async (): Promise<boolean> => {
  try {
    const storedSession = localStorage.getItem('userSession');
    if (storedSession) {
      const session = JSON.parse(storedSession);

      // Check if token expires in the next 5 minutes
      const fiveMinutesFromNow = new Date(Date.now() + 5 * 60 * 1000);
      const expiresAt = new Date(session.expiresAt);

      if (expiresAt < fiveMinutesFromNow) {
        // Attempt to refresh the token using the Authorization header
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/refresh`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.accessToken}`,
          },
        });

        if (response.ok) {
          const data = await response.json();

          // Update the session with the new token
          const newSession = {
            ...session,
            accessToken: data.access_token,
            expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours from now
          };

          localStorage.setItem('userSession', JSON.stringify(newSession));
          return true;
        } else {
          // If refresh failed, remove the session
          localStorage.removeItem('userSession');
          return false;
        }
      }
    }

    return true; // Token is still valid or doesn't need refresh
  } catch (error) {
    console.error('Error refreshing access token:', error);
    return false;
  }
};
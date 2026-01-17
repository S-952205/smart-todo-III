import { ApiResponse } from '@/types';

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private getAccessToken(): string | null {
    if (typeof window !== 'undefined') {
      // Check for token in localStorage
      const storedSession = localStorage.getItem('userSession');
      if (storedSession) {
        try {
          const session = JSON.parse(storedSession);
          return session.accessToken;
        } catch (error) {
          console.error('Error parsing stored session:', error);
          return null;
        }
      }
    }
    return null;
  }

  private setTokens(accessToken: string, refreshToken?: string): void {
    if (typeof window !== 'undefined') {
      const storedSession = localStorage.getItem('userSession');
      if (storedSession) {
        try {
          const session = JSON.parse(storedSession);
          session.accessToken = accessToken;
          if (refreshToken) {
            session.refreshToken = refreshToken;
          }
          // Update expiration time (assuming 24 hours from now)
          session.expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();

          localStorage.setItem('userSession', JSON.stringify(session));
        } catch (error) {
          console.error('Error updating stored session:', error);
        }
      }
    }
  }

  private clearTokens(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('userSession');
      localStorage.removeItem('accessToken');
    }
  }

  private async refreshToken(): Promise<void> {
    // In a real implementation, you would call your backend refresh endpoint
    // For now, we'll simulate a refresh by checking if the user is still logged in
    const storedSession = localStorage.getItem('userSession');
    if (!storedSession) {
      throw new Error('No stored session found');
    }

    try {
      const session = JSON.parse(storedSession);

      // If we have a refresh token, use it to get a new access token
      if (session.refreshToken) {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/refresh`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.refreshToken}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          this.setTokens(data.accessToken, data.refreshToken);
          return;
        }
      }

      // If refresh token is not available or refresh failed, user needs to log in again
      throw new Error('Could not refresh token');
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.clearTokens();
      throw error;
    }
  }

  private async request<T>(url: string, options: RequestInit): Promise<{ success: boolean; data?: T; error?: string; message?: string }> {
    const headers = new Headers(options.headers);
    headers.set('Content-Type', 'application/json');

    const token = this.getAccessToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    const config: RequestInit = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(this.baseURL + url, config);

      // Handle 401 Unauthorized - attempt token refresh
      if (response.status === 401) {
        try {
          await this.refreshToken();
          // Retry the original request with the new token
          const retryHeaders = new Headers(headers);
          retryHeaders.set('Authorization', `Bearer ${this.getAccessToken()}`);

          const retryResponse = await fetch(this.baseURL + url, {
            ...options,
            headers: retryHeaders,
          });

          const retryData = await retryResponse.json();
          return {
            success: retryResponse.ok,
            ...(retryResponse.ok ? { data: retryData } : { error: retryData.message || 'Request failed after token refresh' })
          };
        } catch (refreshError) {
          // If refresh fails, clear stored tokens and redirect to login
          this.clearTokens();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          throw refreshError;
        }
      }

      // Check if response has content before trying to parse JSON
      const contentType = response.headers.get('content-type');
      let data: any = {};

      if (contentType && contentType.includes('application/json')) {
        try {
          data = await response.json();
        } catch (jsonError) {
          // If JSON parsing fails but response is OK, return empty object
          if (response.ok) {
            data = {};
          } else {
            throw jsonError;
          }
        }
      } else if (response.status !== 204) { // 204 No Content
        // For non-JSON responses that aren't 204, try to get text
        try {
          const text = await response.text();
          data = text ? { message: text } : {};
        } catch (textError) {
          // If text parsing also fails but response is OK, return empty object
          if (response.ok) {
            data = {};
          } else {
            throw textError;
          }
        }
      }

      if (response.ok) {
        return { success: true, data: Object.keys(data).length > 0 ? data as T : undefined };
      } else {
        const errorMessage = (data as any)?.message || 'Request failed';
        return { success: false, error: errorMessage, message: errorMessage };
      }
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Network error occurred',
      };
    }
  }

  // GET request
  public async get<T>(url: string, config?: RequestInit): Promise<{ success: boolean; data?: T; error?: string; message?: string }> {
    return this.request<T>(url, { method: 'GET', ...config });
  }

  // POST request
  public async post<T>(url: string, data?: any, config?: RequestInit): Promise<{ success: boolean; data?: T; error?: string; message?: string }> {
    return this.request<T>(url, {
      method: 'POST',
      body: JSON.stringify(data),
      ...config
    });
  }

  // PUT request
  public async put<T>(url: string, data?: any, config?: RequestInit): Promise<{ success: boolean; data?: T; error?: string; message?: string }> {
    return this.request<T>(url, {
      method: 'PUT',
      body: JSON.stringify(data),
      ...config
    });
  }

  // DELETE request
  public async delete<T>(url: string, config?: RequestInit): Promise<{ success: boolean; data?: T; error?: string; message?: string }> {
    return this.request<T>(url, { method: 'DELETE', ...config });
  }
}

// Create a singleton instance
const apiClient = new ApiClient(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

export default apiClient;
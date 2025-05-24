import { create } from 'zustand';
import { AuthResponse, UserRole } from '../types';
import { persist } from 'zustand/middleware';

interface LoginCredentials {
  username: string;
  password: string;
}

interface UserInfo {
  id: string;
  email: string;
  role: UserRole;
}

interface AuthState {
  token: string | null;
  user: UserInfo | null;
  isLoading: boolean;
  error: string | null;
  isInitialized: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  setUser: (user: any) => void;
  clearError: () => void;
}

// Use a constant API URL to ensure it works in production
const API_URL = 'https://vcarpool-dev-api.azurewebsites.net/api/v1';

// Helper to log errors safely
const logError = (message: string, error: unknown) => {
  if (typeof console !== 'undefined') {
    console.error(message, error);
  }
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set: (state: Partial<AuthState>) => void, get: () => AuthState) => ({
      token: null,
      user: null,
      isLoading: false,
      error: null,
      isInitialized: false,
      
      setUser: (user: any) => {
        set({ user });
      },
      
      clearError: () => {
        set({ error: null });
      },

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });
        try {
          console.log('Attempting login to API:', API_URL);
          
          const response = await fetch(`${API_URL}/auth/token`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
              username: credentials.username,
              password: credentials.password,
            }),
            // Add credentials to handle cookies if needed
            credentials: 'include'
          });

          console.log('Login response status:', response.status);

          if (!response.ok) {
            const errorText = await response.text();
            console.error('Login failed:', errorText);
            throw new Error(response.status === 401 ? 'Invalid credentials' : `Login failed: ${response.statusText}`);
          }

          const data: AuthResponse = await response.json();
          console.log('Login successful, received token');
          
          set({ 
            token: data.access_token, 
            user: {
              id: data.user_id,
              email: data.email,
              role: data.role
            },
            isLoading: false,
            isInitialized: true
          });
        } catch (error) {
          logError('Login error:', error);
          set({
            error: error instanceof Error ? error.message : 'An error occurred during login',
            isLoading: false,
            isInitialized: true
          });
          throw error; // Re-throw to handle in the UI
        }
      },

      logout: () => {
        console.log('Logging out user');
        set({ token: null, user: null });
        // Clear any session cookies if needed
        if (typeof document !== 'undefined') {
          document.cookie.split(';').forEach(cookie => {
            document.cookie = cookie
              .replace(/^ +/, '')
              .replace(/=.*/, `=;expires=${new Date().toUTCString()};path=/`);
          });
        }
      },

      changePassword: async (currentPassword: string, newPassword: string) => {
        const { token } = get();
        if (!token) {
          const error = 'You must be logged in to change your password';
          set({ error });
          throw new Error(error);
        }

        set({ isLoading: true, error: null });
        try {
          console.log('Attempting to change password');
          
          const response = await fetch(`${API_URL}/users/me/password`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({
              current_password: currentPassword,
              new_password: newPassword,
            }),
          });

          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to change password');
          }

          console.log('Password changed successfully');
          set({ isLoading: false });
        } catch (error) {
          logError('Password change error:', error);
          const errorMessage = error instanceof Error ? error.message : 'Failed to change password';
          set({
            error: errorMessage,
            isLoading: false
          });
          throw error;
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state: AuthState) => ({ 
        token: state.token, 
        user: state.user,
        isInitialized: state.isInitialized 
      }),
      // Add a version number to handle storage format changes
      version: 1,
    }
  )
);
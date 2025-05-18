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
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  setUser: (user: any) => void;
}

type AuthStoreActions = {
  set: (state: Partial<AuthState>) => void;
  get: () => AuthState;
};

export const useAuthStore = create<AuthState>()(
  persist(    (set: (state: Partial<AuthState>) => void, get: () => AuthState) => ({
      token: null,
      user: null,
      isLoading: false,
      error: null,
      
      setUser: (user: any) => {
        set({ user });
      },

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });
        try {
          const apiUrl = typeof window !== 'undefined' 
            ? (window.location.origin + '/api/v1') 
            : 'http://localhost:8000/api/v1';
            
          const response = await fetch(`${apiUrl}/auth/token`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
              username: credentials.username,
              password: credentials.password,
            }),
          });

          if (!response.ok) {
            throw new Error('Invalid credentials');
          }

          const data: AuthResponse = await response.json();
          set({ 
            token: data.access_token, 
            user: {
              id: data.user_id,
              email: data.email,
              role: data.role
            },
            isLoading: false 
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'An error occurred during login',
            isLoading: false
          });
        }
      },

      logout: () => {
        set({ token: null, user: null });
      },

      changePassword: async (currentPassword: string, newPassword: string) => {
        const { token } = get();
        if (!token) {
          set({ error: 'You must be logged in to change your password' });
          return;
        }

        set({ isLoading: true, error: null });
        try {
          const apiUrl = typeof window !== 'undefined' 
            ? (window.location.origin + '/api/v1') 
            : 'http://localhost:8000/api/v1';
            
          const response = await fetch(`${apiUrl}/users/me/password`, {
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
            const data = await response.json();
            throw new Error(data.detail || 'Failed to change password');
          }

          set({ isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to change password',
            isLoading: false
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state: AuthState) => ({ token: state.token, user: state.user }),
    }
  )
); 
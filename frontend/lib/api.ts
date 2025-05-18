import { AuthResponse, User, UserRole } from '../types';

const API_URL = typeof window !== 'undefined' 
  ? (window.location.origin + '/api/v1')
  : 'http://localhost:8000/api/v1';

interface LoginCredentials {
  username: string;
  password: string;
}

interface UserCreate {
  email: string;
  full_name: string;
  role: UserRole;
  initial_password: string;
  phone_number?: string;
  is_active_driver?: boolean;
  home_address?: string;
}

interface PasswordChange {
  current_password: string;
  new_password: string;
}

// Helper function to get auth token from store
const getToken = (): string | null => {
  if (typeof window !== 'undefined') {
    const authData = localStorage.getItem('auth-storage');
    if (authData) {
      try {
        const parsed = JSON.parse(authData);
        return parsed.state?.token || null;
      } catch (e) {
        return null;
      }
    }
  }
  return null;
};

// API request helpers
const fetchApi = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<any> => {
  const token = getToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  } as Record<string, string>;
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });
  
  // Handle unauthorized
  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth-storage');
      window.location.href = '/login';
    }
    throw new Error('Unauthorized');
  }
  
  // Handle other errors
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'API request failed');
  }
  
  // Return data for successful responses
  if (response.status !== 204) {
    return await response.json();
  }
  
  return null;
};

export const auth = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await fetch(`${API_URL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    return await response.json();
  },
};

export const users = {
  me: async (): Promise<User> => {
    return fetchApi('/users/me');
  },
  
  create: async (userData: UserCreate): Promise<User> => {
    return fetchApi('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },
  
  updateMe: async (userData: Partial<User>): Promise<User> => {
    return fetchApi('/users/me', {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  },
  
  changePassword: async (passwordData: PasswordChange): Promise<void> => {
    return fetchApi('/users/me/password', {
      method: 'PUT',
      body: JSON.stringify(passwordData),
    });
  },
  
  createAdmin: async (userData: UserCreate): Promise<User> => {
    return fetchApi('/admin/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },
};

export const scheduleTemplates = {
  getAll: async () => {
    return fetchApi('/schedule-templates');
  },
  
  getById: async (id: string) => {
    return fetchApi(`/schedule-templates/${id}`);
  },
  
  create: async (template: any) => {
    return fetchApi('/schedule-templates', {
      method: 'POST',
      body: JSON.stringify(template),
    });
  },
  
  update: async (id: string, template: any) => {
    return fetchApi(`/schedule-templates/${id}`, {
      method: 'PUT',
      body: JSON.stringify(template),
    });
  },
  
  delete: async (id: string) => {
    return fetchApi(`/schedule-templates/${id}`, {
      method: 'DELETE',
    });
  },
};

export const driverPreferences = {
  submit: async (preferences: any, weekStartDate: string) => {
    return fetchApi(`/parent/weekly-preferences?week_start_date=${weekStartDate}`, {
      method: 'POST',
      body: JSON.stringify(preferences),
    });
  },
  
  get: async (weekStartDate: string) => {
    return fetchApi(`/parent/weekly-preferences?week_start_date=${weekStartDate}`);
  },
};

export const scheduling = {
  generateSchedule: async (weekStartDate: string) => {
    return fetchApi(`/admin/generate-schedule?week_start_date=${weekStartDate}`, {
      method: 'POST',
    });
  },
  
  getSchedule: async (weekStartDate: string) => {
    return fetchApi(`/admin/schedule?week_start_date=${weekStartDate}`);
  },
};

export const swapRequests = {
  create: async (rideAssignmentId: string, requestedDriverId: string) => {
    return fetchApi('/swap-requests', {
      method: 'POST',
      body: JSON.stringify({ 
        ride_assignment_id: rideAssignmentId, 
        requested_driver_id: requestedDriverId 
      }),
    });
  },
  
  list: async (status?: string) => {
    const endpoint = status ? `/swap-requests?status=${status}` : '/swap-requests';
    return fetchApi(endpoint);
  },
  
  accept: async (requestId: string) => {
    return fetchApi(`/swap-requests/${requestId}/accept`, {
      method: 'PUT',
    });
  },
  
  reject: async (requestId: string) => {
    return fetchApi(`/swap-requests/${requestId}/reject`, {
      method: 'PUT',
    });
  },
};
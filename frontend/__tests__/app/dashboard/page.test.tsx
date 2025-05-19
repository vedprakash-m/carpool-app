import { render, screen, waitFor } from '@testing-library/react';
import DashboardPage from '../../../app/dashboard/page';
import { UserRole } from '../../../types';

// Mock the auth store
jest.mock('../../../store/auth', () => ({
  useAuthStore: jest.fn(() => ({
    user: {
      id: '123',
      email: 'test@example.com',
      full_name: 'Test User',
      role: UserRole.ADMIN,
    },
    isAuthenticated: true,
  })),
}));

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
  usePathname: () => '/dashboard',
}));

describe('DashboardPage', () => {
  test('renders welcome message', () => {
    render(<DashboardPage />);
    
    expect(screen.getByText(/welcome/i)).toBeInTheDocument();
    expect(screen.getByText(/Test User/i)).toBeInTheDocument();
  });
  
  test('renders admin dashboard components when user is admin', () => {
    render(<DashboardPage />);
    
    // Check for admin-specific elements
    expect(screen.getByText(/system statistics/i)).toBeInTheDocument();
    expect(screen.getByText(/user management/i)).toBeInTheDocument();
  });
  
  test('renders different dashboard for parent role', () => {
    // Override the mock for this test
    const { useAuthStore } = require('../../../store/auth');
    useAuthStore.mockReturnValue({
      user: {
        id: '123',
        email: 'parent@example.com',
        full_name: 'Parent User',
        role: UserRole.PARENT,
      },
      isAuthenticated: true,
    });
    
    render(<DashboardPage />);
    
    // Check for parent-specific elements
    expect(screen.getByText(/your rides/i)).toBeInTheDocument();
    expect(screen.getByText(/swap requests/i)).toBeInTheDocument();
    expect(screen.queryByText(/user management/i)).not.toBeInTheDocument();
  });
});

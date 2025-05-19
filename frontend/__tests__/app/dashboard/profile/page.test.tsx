import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProfilePage from '../../../../app/dashboard/profile/page';
import { UserRole } from '../../../../types';

// Mock the auth store
jest.mock('../../../../store/auth', () => ({
  useAuthStore: jest.fn(() => ({
    user: {
      id: '123',
      email: 'user@example.com',
      full_name: 'Test User',
      role: UserRole.PARENT,
      is_active_driver: true,
    },
    isAuthenticated: true,
  })),
}));

// Mock the API functions
jest.mock('../../../../lib/api', () => ({
  users: {
    getProfile: jest.fn().mockResolvedValue({
      id: '123',
      email: 'user@example.com',
      full_name: 'Test User',
      role: UserRole.PARENT,
      is_active_driver: true,
      address: '123 Main St',
      phone_number: '555-1234',
    }),
  },
}));

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('ProfilePage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders user profile information', async () => {
    render(<ProfilePage />);
    
    // Wait for profile data to load
    expect(await screen.findByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('user@example.com')).toBeInTheDocument();
    expect(screen.getByText('PARENT')).toBeInTheDocument();
    expect(screen.getByText('123 Main St')).toBeInTheDocument();
    expect(screen.getByText('555-1234')).toBeInTheDocument();
  });
  
  test('displays active driver status', async () => {
    render(<ProfilePage />);
    
    expect(await screen.findByText(/active driver/i)).toBeInTheDocument();
  });
  
  test('renders edit profile button', async () => {
    render(<ProfilePage />);
    
    const editButton = await screen.findByRole('link', { name: /edit profile/i });
    expect(editButton).toBeInTheDocument();
    expect(editButton.getAttribute('href')).toBe('/dashboard/profile/edit');
  });
  
  test('renders change password button', async () => {
    render(<ProfilePage />);
    
    const passwordButton = await screen.findByRole('link', { name: /change password/i });
    expect(passwordButton).toBeInTheDocument();
    expect(passwordButton.getAttribute('href')).toBe('/dashboard/profile/change-password');
  });
  
  test('handles loading state', () => {
    // Override API to simulate loading
    const { users } = require('../../../../lib/api');
    users.getProfile.mockImplementationOnce(() => new Promise(() => {})); // Never resolves
    
    render(<ProfilePage />);
    
    expect(screen.getByText(/loading profile/i)).toBeInTheDocument();
  });
  
  test('handles error state', async () => {
    // Override API to simulate error
    const { users } = require('../../../../lib/api');
    users.getProfile.mockRejectedValueOnce(new Error('Failed to load profile'));
    
    render(<ProfilePage />);
    
    expect(await screen.findByText(/error loading profile/i)).toBeInTheDocument();
  });
});

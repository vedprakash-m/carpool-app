import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CreateUserPage from '../../../../app/dashboard/users/create/page';
import { UserRole } from '../../../../types';

// Mock the auth store
jest.mock('../../../../store/auth', () => ({
  useAuthStore: jest.fn(() => ({
    user: {
      id: '123',
      email: 'admin@example.com',
      full_name: 'Admin User',
      role: UserRole.ADMIN,
    },
    isAuthenticated: true,
  })),
}));

// Mock the API functions
jest.mock('../../../../lib/api', () => ({
  users: {
    create: jest.fn().mockResolvedValue({ id: 'new-user-id', email: 'newuser@example.com' }),
  },
}));

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('CreateUserPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders user creation form', () => {
    render(<CreateUserPage />);
    
    expect(screen.getByRole('heading', { name: /create new user/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/role/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/initial password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create user/i })).toBeInTheDocument();
  });
  
  test('submits form with user data', async () => {
    const { users } = require('../../../../lib/api');
    const { useRouter } = require('next/navigation');
    const mockPush = jest.fn();
    useRouter.mockReturnValue({ push: mockPush });
    
    render(<CreateUserPage />);
    
    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/email/i), 'newuser@example.com');
    await user.type(screen.getByLabelText(/full name/i), 'New Test User');
    await user.selectOptions(screen.getByLabelText(/role/i), 'PARENT');
    await user.type(screen.getByLabelText(/initial password/i), 'SecurePassword123!');
    
    await user.click(screen.getByRole('button', { name: /create user/i }));
    
    await waitFor(() => {
      expect(users.create).toHaveBeenCalledWith({
        email: 'newuser@example.com',
        full_name: 'New Test User',
        role: 'PARENT',
        initial_password: 'SecurePassword123!',
        is_active_driver: expect.any(Boolean)
      });
    });
    
    // Check that we navigate to users list after successful creation
    expect(mockPush).toHaveBeenCalledWith('/dashboard/users');
  });
  
  test('displays validation errors', async () => {
    render(<CreateUserPage />);
    
    const user = userEvent.setup();
    // Enter invalid email
    await user.type(screen.getByLabelText(/email/i), 'not-an-email');
    await user.click(screen.getByRole('button', { name: /create user/i }));
    
    expect(await screen.findByText(/invalid email address/i)).toBeInTheDocument();
  });
  
  test('handles API errors', async () => {
    const { users } = require('../../../../lib/api');
    users.create.mockRejectedValueOnce(new Error('Email already exists'));
    
    render(<CreateUserPage />);
    
    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/email/i), 'existing@example.com');
    await user.type(screen.getByLabelText(/full name/i), 'Existing User');
    await user.selectOptions(screen.getByLabelText(/role/i), 'PARENT');
    await user.type(screen.getByLabelText(/initial password/i), 'SecurePassword123!');
    
    await user.click(screen.getByRole('button', { name: /create user/i }));
    
    expect(await screen.findByText(/email already exists/i)).toBeInTheDocument();
  });
});

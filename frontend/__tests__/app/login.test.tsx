import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginPage from '../../app/login/page';

// Mock the auth store
jest.mock('../../store/auth', () => ({
  useAuthStore: jest.fn(() => ({
    login: jest.fn(),
    isLoading: false,
    error: null,
  })),
}));

// Mock the router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('LoginPage', () => {
  test('renders login form', () => {
    render(<LoginPage />);
    
    // Check if form elements are rendered
    expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  test('handles form submission', async () => {
    const mockLogin = jest.fn();
    const { useAuthStore } = require('../../store/auth');
    useAuthStore.mockReturnValue({
      login: mockLogin,
      isLoading: false,
      error: null,
    });
    
    render(<LoginPage />);
    
    // Fill out form
    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    
    // Submit form
    await user.click(screen.getByRole('button', { name: /sign in/i }));
    
    // Check if login was called with correct credentials
    expect(mockLogin).toHaveBeenCalledWith({
      username: 'test@example.com',
      password: 'password123',
    });
  });

  test('displays error message when login fails', () => {
    const { useAuthStore } = require('../../store/auth');
    useAuthStore.mockReturnValue({
      login: jest.fn(),
      isLoading: false,
      error: 'Invalid credentials',
    });
    
    render(<LoginPage />);
    
    // Check if error message is displayed
    expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
  });

  test('displays loading state during login', () => {
    const { useAuthStore } = require('../../store/auth');
    useAuthStore.mockReturnValue({
      login: jest.fn(),
      isLoading: true,
      error: null,
    });
    
    render(<LoginPage />);
    
    // Check if loading indicator is displayed
    expect(screen.getByRole('button', { name: /signing in/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /signing in/i })).toBeDisabled();
  });
});

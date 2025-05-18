import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SwapRequest, UserRole } from '../../../types';
import SwapRequestsPage from '../../../app/dashboard/swap-requests/page';

// Mock the auth store
jest.mock('../../../store/auth', () => ({
  useAuthStore: jest.fn(() => ({
    user: {
      id: '123',
      email: 'parent@example.com',
      full_name: 'Test Parent',
      role: UserRole.PARENT,
      is_active_driver: true,
    },
  })),
}));

// Mock the API functions
jest.mock('../../../lib/api', () => ({
  swapRequests: {
    list: jest.fn(),
    approve: jest.fn(),
    reject: jest.fn(),
  }
}));

const mockSwapRequests = [
  {
    id: 'req1',
    requester_id: 'user1',
    requester_name: 'John Doe',
    requested_date: '2025-05-20',
    status: 'PENDING',
    created_at: '2025-05-15T10:00:00Z',
    reason: 'Doctor appointment'
  },
  {
    id: 'req2',
    requester_id: 'user2',
    requester_name: 'Jane Smith',
    requested_date: '2025-05-25',
    status: 'PENDING',
    created_at: '2025-05-16T14:30:00Z',
    reason: 'Family event'
  }
] as SwapRequest[];

describe('SwapRequestsPage', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Default mock implementations
    const { swapRequests } = require('../../../lib/api');
    swapRequests.list.mockResolvedValue(mockSwapRequests);
    swapRequests.approve.mockResolvedValue({ success: true });
    swapRequests.reject.mockResolvedValue({ success: true });
  });

  test('renders loading state initially', () => {
    render(<SwapRequestsPage />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('renders swap requests after loading', async () => {
    render(<SwapRequestsPage />);
    
    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Check if requests are displayed
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('Doctor appointment')).toBeInTheDocument();
    expect(screen.getByText('Family event')).toBeInTheDocument();
  });

  // Add more tests here for approving, rejecting, etc.
});

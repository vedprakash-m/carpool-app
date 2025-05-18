import { enableFetchMocks } from 'jest-fetch-mock';
enableFetchMocks();

// We need to mock fetch before importing the API
import { auth, users, swapRequests } from '../../lib/api';
import { UserRole } from '../../types';

describe('API Utilities', () => {
  beforeEach(() => {
    // Reset fetch mocks
    fetchMock.resetMocks();
    
    // Clear localStorage mock
    window.localStorage.clear();
    window.localStorage.getItem.mockClear();
    window.localStorage.setItem.mockClear();
  });

  describe('auth API', () => {
    test('login calls correct endpoint with credentials', async () => {
      const mockResponse = { 
        access_token: 'mock-token', 
        user: { 
          id: '123', 
          email: 'test@example.com',
          role: UserRole.PARENT
        }
      };
      fetchMock.mockResponseOnce(JSON.stringify(mockResponse));

      const credentials = { username: 'test@example.com', password: 'password' };
      const response = await auth.login(credentials);

      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/auth/login'), {
        method: 'POST',
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(credentials)
      });
      expect(response).toEqual(mockResponse);
    });

    test('logout clears auth data', async () => {
      fetchMock.mockResponseOnce(JSON.stringify({ success: true }));

      // Mock that we have a token
      window.localStorage.getItem.mockReturnValueOnce(JSON.stringify({ 
        state: { token: 'mock-token' } 
      }));

      await auth.logout();

      // Check localStorage was cleared
      expect(window.localStorage.removeItem).toHaveBeenCalledWith('auth-storage');
      
      // Check API was called
      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/auth/logout'), {
        method: 'POST',
        headers: expect.objectContaining({ 'Authorization': 'Bearer mock-token' }),
      });
    });
  });

  describe('users API', () => {
    test('list gets all users with authorization', async () => {
      const mockUsers = [{ id: '1', name: 'Test User' }];
      fetchMock.mockResponseOnce(JSON.stringify(mockUsers));
      
      // Mock that we have a token
      window.localStorage.getItem.mockReturnValueOnce(JSON.stringify({ 
        state: { token: 'mock-token' } 
      }));

      const response = await users.list();

      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/users'), {
        method: 'GET',
        headers: expect.objectContaining({ 'Authorization': 'Bearer mock-token' }),
      });
      expect(response).toEqual(mockUsers);
    });
  });

  describe('swapRequests API', () => {
    test('list gets all swap requests', async () => {
      const mockRequests = [{ id: '1', requester_id: 'user1' }];
      fetchMock.mockResponseOnce(JSON.stringify(mockRequests));
      
      // Mock that we have a token
      window.localStorage.getItem.mockReturnValueOnce(JSON.stringify({ 
        state: { token: 'mock-token' } 
      }));

      const response = await swapRequests.list();

      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/swap-requests'), {
        method: 'GET',
        headers: expect.objectContaining({ 'Authorization': 'Bearer mock-token' }),
      });
      expect(response).toEqual(mockRequests);
    });
  });
});

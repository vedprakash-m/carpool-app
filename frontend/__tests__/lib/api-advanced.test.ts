import { enableFetchMocks } from 'jest-fetch-mock';
enableFetchMocks();

// Import the API functions
import { auth, users, swapRequests, schedules, statistics } from '../../lib/api';
import { UserRole } from '../../types';

describe('Advanced API Utilities', () => {
  beforeEach(() => {
    // Reset fetch mocks
    fetchMock.resetMocks();
    
    // Clear localStorage mock
    window.localStorage.clear();
    window.localStorage.getItem.mockClear();
    window.localStorage.setItem.mockClear();
  });

  describe('schedules API', () => {
    test('generate creates a new schedule', async () => {
      const mockSchedule = [
        { id: 'ride1', driver_parent_id: 'parent1', date: '2025-06-01' },
        { id: 'ride2', driver_parent_id: 'parent2', date: '2025-06-01' }
      ];
      fetchMock.mockResponseOnce(JSON.stringify(mockSchedule));
      
      // Mock that we have a token
      window.localStorage.getItem.mockReturnValueOnce(JSON.stringify({ 
        state: { token: 'mock-token' } 
      }));

      const params = {
        template_id: 'template1',
        start_date: '2025-06-01',
        end_date: '2025-06-07'
      };
      const response = await schedules.generate(params);

      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/schedules/generate'), {
        method: 'POST',
        headers: expect.objectContaining({ 
          'Authorization': 'Bearer mock-token',
          'Content-Type': 'application/json'
        }),
        body: JSON.stringify(params)
      });
      expect(response).toEqual(mockSchedule);
    });
    
    test('getSchedule fetches schedule for specific date range', async () => {
      const mockSchedule = [
        { id: 'ride1', driver_parent_id: 'parent1', date: '2025-06-01' },
        { id: 'ride2', driver_parent_id: 'parent2', date: '2025-06-02' }
      ];
      fetchMock.mockResponseOnce(JSON.stringify(mockSchedule));
      
      // Mock that we have a token
      window.localStorage.getItem.mockReturnValueOnce(JSON.stringify({ 
        state: { token: 'mock-token' } 
      }));

      const response = await schedules.getSchedule('2025-06-01', '2025-06-07');

      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/schedules?start_date=2025-06-01&end_date=2025-06-07'), 
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({ 'Authorization': 'Bearer mock-token' })
        })
      );
      expect(response).toEqual(mockSchedule);
    });
    
    test('getUserRides fetches rides for specific user', async () => {
      const mockRides = [
        { id: 'ride1', driver_parent_id: 'parent1', date: '2025-06-01' },
        { id: 'ride2', driver_parent_id: 'parent1', date: '2025-06-02' }
      ];
      fetchMock.mockResponseOnce(JSON.stringify(mockRides));
      
      // Mock that we have a token
      window.localStorage.getItem.mockReturnValueOnce(JSON.stringify({ 
        state: { token: 'mock-token' } 
      }));

      const response = await schedules.getUserRides('parent1', '2025-06-01', '2025-06-07');

      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/schedules/user/parent1?start_date=2025-06-01&end_date=2025-06-07'), 
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({ 'Authorization': 'Bearer mock-token' })
        })
      );
      expect(response).toEqual(mockRides);
    });
  });

  describe('statistics API', () => {
    test('getDriverStats fetches statistics for drivers', async () => {
      const mockStats = [
        { driver_id: 'parent1', rides_count: 10, student_count: 25 },
        { driver_id: 'parent2', rides_count: 8, student_count: 20 }
      ];
      fetchMock.mockResponseOnce(JSON.stringify(mockStats));
      
      // Mock that we have a token
      window.localStorage.getItem.mockReturnValueOnce(JSON.stringify({ 
        state: { token: 'mock-token' } 
      }));

      const response = await statistics.getDriverStats();

      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/statistics/drivers'), {
        method: 'GET',
        headers: expect.objectContaining({ 'Authorization': 'Bearer mock-token' })
      });
      expect(response).toEqual(mockStats);
    });
    
    test('getSystemStats fetches overall system statistics', async () => {
      const mockStats = {
        total_rides: 120,
        active_drivers: 15,
        active_students: 45,
        rides_this_month: 30
      };
      fetchMock.mockResponseOnce(JSON.stringify(mockStats));
      
      // Mock that we have a token
      window.localStorage.getItem.mockReturnValueOnce(JSON.stringify({ 
        state: { token: 'mock-token' } 
      }));

      const response = await statistics.getSystemStats();

      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/statistics/system'), {
        method: 'GET',
        headers: expect.objectContaining({ 'Authorization': 'Bearer mock-token' })
      });
      expect(response).toEqual(mockStats);
    });
  });

  describe('auth refresh token', () => {
    test('refreshToken gets a new token using refresh token', async () => {
      const mockResponse = { 
        access_token: 'new-token',
        refresh_token: 'new-refresh-token' 
      };
      fetchMock.mockResponseOnce(JSON.stringify(mockResponse));
      
      // Mock that we have refresh token
      window.localStorage.getItem.mockReturnValueOnce(JSON.stringify({ 
        state: { 
          token: 'old-token',
          refreshToken: 'old-refresh-token' 
        } 
      }));

      const response = await auth.refreshToken();

      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/auth/refresh'), {
        method: 'POST',
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ refresh_token: 'old-refresh-token' })
      });
      
      // Check localStorage was updated with new tokens
      expect(window.localStorage.setItem).toHaveBeenCalledWith(
        'auth-storage', 
        expect.stringContaining('new-token')
      );
      expect(window.localStorage.setItem).toHaveBeenCalledWith(
        'auth-storage', 
        expect.stringContaining('new-refresh-token')
      );
      
      expect(response).toEqual(mockResponse);
    });
    
    test('refreshToken handles failure gracefully', async () => {
      fetchMock.mockRejectOnce(new Error('Invalid refresh token'));
      
      // Mock that we have refresh token
      window.localStorage.getItem.mockReturnValueOnce(JSON.stringify({ 
        state: { 
          token: 'old-token',
          refreshToken: 'invalid-refresh-token' 
        } 
      }));

      try {
        await auth.refreshToken();
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.message).toContain('Invalid refresh token');
      }
      
      // Check localStorage was cleared on refresh token failure
      expect(window.localStorage.removeItem).toHaveBeenCalledWith('auth-storage');
    });
  });
});

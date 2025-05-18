'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../store/auth';
import { UserRole } from '../../../types';
import { statistics } from '../../../lib/api';

export default function StatisticsPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [stats, setStats] = useState({
    totalRides: 0,
    byDriver: [],
    byRouteType: { TO_SCHOOL: 0, FROM_SCHOOL: 0 },
    byDayOfWeek: [0, 0, 0, 0, 0, 0, 0]
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeframe, setTimeframe] = useState('month');

  useEffect(() => {
    // Only admins can access this page
    if (user?.role !== UserRole.ADMIN) {
      router.push('/dashboard');
      return;
    }

    const fetchStatistics = async () => {
      try {
        // Fetch real data from the API
        const data = await statistics.getCarpoolStats(timeframe);
        setStats(data);
      } catch (err) {
        // Fallback to mock data in case of API failure
        setStats(generateMockStatistics());
        setError('Could not load real-time statistics. Showing sample data instead.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStatistics();
  }, [user, router, timeframe]);

  // Fallback function for generating mock data
  const generateMockStatistics = () => {
    const drivers = ['John Smith', 'Mary Johnson', 'Robert Williams', 'Sarah Brown', 'Michael Davis'];
    const driverStats = drivers.map(name => ({
      name,
      rides: Math.floor(Math.random() * 20) + 5
    }));
    
    // Sort by number of rides
    driverStats.sort((a, b) => b.rides - a.rides);
    
    return {
      totalRides: driverStats.reduce((sum, driver) => sum + driver.rides, 0),
      byDriver: driverStats,
      byRouteType: {
        TO_SCHOOL: Math.floor(Math.random() * 50) + 30,
        FROM_SCHOOL: Math.floor(Math.random() * 50) + 30
      },
      byDayOfWeek: [0, 
        Math.floor(Math.random() * 20) + 10, 
        Math.floor(Math.random() * 20) + 10, 
        Math.floor(Math.random() * 20) + 10, 
        Math.floor(Math.random() * 20) + 10, 
        Math.floor(Math.random() * 20) + 10,
        0
      ]
    };
  };

  const getDayName = (dayIndex) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[dayIndex];
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4">Loading statistics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center">
        <div className="p-4 bg-red-100 text-red-700 rounded-md">
          <p>Error: {error}</p>
          <button 
            className="mt-2 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Calculate the maximum value for scaling bars
  const maxDriverRides = Math.max(...stats.byDriver.map(d => d.rides));
  const maxDayRides = Math.max(...stats.byDayOfWeek);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-semibold mb-6">Carpool Statistics</h1>
      
      <div className="mb-6">
        <label htmlFor="timeframe" className="block text-sm font-medium text-gray-700 mb-1">
          Timeframe:
        </label>
        <select
          id="timeframe"
          className="w-full md:w-auto px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={timeframe}
          onChange={(e) => setTimeframe(e.target.value)}
        >
          <option value="week">Past Week</option>
          <option value="month">Past Month</option>
          <option value="quarter">Past 3 Months</option>
          <option value="year">Past Year</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Summary Cards */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <p className="text-gray-500 text-sm">Total Rides</p>
              <p className="text-3xl font-bold text-blue-600">{stats.totalRides}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <p className="text-gray-500 text-sm">Active Drivers</p>
              <p className="text-3xl font-bold text-green-600">{stats.byDriver.length}</p>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4 text-center">
              <p className="text-gray-500 text-sm">To School</p>
              <p className="text-3xl font-bold text-yellow-600">{stats.byRouteType.TO_SCHOOL}</p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <p className="text-gray-500 text-sm">From School</p>
              <p className="text-3xl font-bold text-purple-600">{stats.byRouteType.FROM_SCHOOL}</p>
            </div>
          </div>
        </div>

        {/* Rides by Driver */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">Rides by Driver</h2>
          <div className="space-y-3">
            {stats.byDriver.map((driver, index) => (
              <div key={index} className="flex items-center">
                <div className="w-1/4 text-sm">{driver.name}</div>
                <div className="w-3/4">
                  <div className="relative h-6">
                    <div 
                      className="absolute top-0 left-0 bg-blue-500 h-6 rounded-sm"
                      style={{ width: `${(driver.rides / maxDriverRides) * 100}%` }}
                    ></div>
                    <div className="absolute inset-0 flex items-center justify-end px-2 text-sm">
                      {driver.rides} rides
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Rides by Day of Week */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">Rides by Day of Week</h2>
          <div className="flex items-end h-64 mt-6 space-x-2">
            {stats.byDayOfWeek.map((count, index) => (
              index > 0 && index < 6 ? (
                <div key={index} className="flex-1 flex flex-col items-center">
                  <div 
                    className="w-full bg-indigo-500 rounded-t-sm"
                    style={{ height: `${(count / maxDayRides) * 80}%` }}
                  ></div>
                  <div className="text-xs mt-2">{getDayName(index).substring(0, 3)}</div>
                  <div className="text-xs text-gray-500">{count}</div>
                </div>
              ) : null
            ))}
          </div>
        </div>

        {/* Route Type Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">Route Type Distribution</h2>
          <div className="flex justify-center items-center h-64">
            <div className="relative w-48 h-48">
              {/* This would be a proper chart in a real implementation */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="rounded-full overflow-hidden w-full h-full">
                  <div 
                    className="bg-yellow-400 h-full"
                    style={{ 
                      width: '100%', 
                      clipPath: `polygon(50% 50%, 50% 0%, ${50 + 50 * (stats.byRouteType.TO_SCHOOL / (stats.byRouteType.TO_SCHOOL + stats.byRouteType.FROM_SCHOOL)))}% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%, 50% 0%)` 
                    }}
                  ></div>
                  <div 
                    className="bg-purple-400 h-full"
                    style={{ 
                      width: '100%', 
                      marginTop: `-100%`,
                      clipPath: `polygon(50% 50%, ${50 + 50 * (stats.byRouteType.TO_SCHOOL / (stats.byRouteType.TO_SCHOOL + stats.byRouteType.FROM_SCHOOL))}% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%)` 
                    }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
          <div className="flex justify-center space-x-8 mt-4">
            <div className="flex items-center">
              <div className="w-4 h-4 bg-yellow-400 rounded-sm mr-2"></div>
              <span className="text-sm">To School ({stats.byRouteType.TO_SCHOOL})</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-purple-400 rounded-sm mr-2"></div>
              <span className="text-sm">From School ({stats.byRouteType.FROM_SCHOOL})</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

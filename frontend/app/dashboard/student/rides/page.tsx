'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../../store/auth';
import { UserRole } from '../../../../types';
import { student } from '../../../../lib/api';

export default function StudentRidesPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [rides, setRides] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [weekStartDate, setWeekStartDate] = useState('');

  useEffect(() => {
    // Only students can access this page
    if (user?.role !== UserRole.STUDENT) {
      router.push('/dashboard');
      return;
    }

    // Calculate current week's Monday as the default week start date
    const today = new Date();
    const monday = new Date(today);
    monday.setDate(today.getDate() - today.getDay() + 1);
    monday.setHours(0, 0, 0, 0);
    setWeekStartDate(monday.toISOString().split('T')[0]);

    const fetchStudentRides = async () => {
      try {
        // Fetch the student's rides from the API
        const data = await student.getRides(monday.toISOString().split('T')[0]);
        setRides(data);
      } catch (err) {
        setError(err.message || 'Failed to fetch rides');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStudentRides();
  }, [user, router]);

  const handleDateChange = async (e) => {
    const newDate = e.target.value;
    setWeekStartDate(newDate);
    setIsLoading(true);
    
    try {
      // Fetch rides for the new week
      const data = await student.getRides(newDate);
      setRides(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch rides');
    } finally {
      setIsLoading(false);
    }
  };

  const getDayName = (dayIndex) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[dayIndex];
  };

  const formatTime = (timeString) => {
    const date = new Date(`2000-01-01T${timeString}`);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4">Loading your rides...</p>
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

  return (
    <div className="p-4">
      <h1 className="text-2xl font-semibold mb-4">Your Carpool Schedule</h1>

      <div className="mb-6">
        <label htmlFor="week-select" className="block text-sm font-medium text-gray-700 mb-1">
          Week Starting:
        </label>
        <input
          type="date"
          id="week-select"
          className="w-full md:w-auto px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={weekStartDate}
          onChange={handleDateChange}
        />
      </div>

      {rides.length === 0 ? (
        <div className="p-6 bg-gray-50 rounded-lg text-center">
          <p className="text-gray-600">No rides scheduled for this week.</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-5 grid-cols-1">
          {[1, 2, 3, 4, 5].map((dayOfWeek) => (
            <div key={dayOfWeek} className="bg-white rounded-lg shadow p-4">
              <h2 className="font-semibold text-lg border-b pb-2 mb-3">{getDayName(dayOfWeek)}</h2>
              
              {rides.filter(ride => ride.day_of_week === dayOfWeek).map(ride => (
                <div key={ride.id} className="mb-3 p-3 bg-gray-50 rounded-md">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium">{formatTime(ride.start_time)} - {formatTime(ride.end_time)}</span>
                    <span className={`px-2 py-1 rounded text-xs ${
                      ride.route_type === 'TO_SCHOOL' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                    }`}>
                      {ride.route_type === 'TO_SCHOOL' ? 'To School' : 'From School'}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mb-1">
                    <span className="font-medium">Driver:</span> {ride.driver_name}
                  </div>
                  <div className="text-xs text-gray-500">
                    <span className="font-medium">Phone:</span> {ride.driver_phone}
                  </div>
                </div>
              ))}
              
              {rides.filter(ride => ride.day_of_week === dayOfWeek).length === 0 && (
                <p className="text-sm text-gray-500 italic">No rides scheduled</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

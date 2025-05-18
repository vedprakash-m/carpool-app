'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../store/auth';
import { scheduling, scheduleTemplates } from '../../../lib/api';
import { UserRole, RideAssignment, WeeklyScheduleTemplateSlot } from '../../../types';

export default function MyRidesPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [rides, setRides] = useState<RideAssignment[]>([]);
  const [templateMap, setTemplateMap] = useState<Record<string, WeeklyScheduleTemplateSlot>>({});
  const [weekStartDate, setWeekStartDate] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Only parents can access this page
    if (user?.role !== UserRole.PARENT) {
      router.push('/dashboard');
      return;
    }

    // Calculate this week's Monday as the default week start date
    const today = new Date();
    const thisMonday = new Date(today);
    thisMonday.setDate(today.getDate() - today.getDay() + (today.getDay() === 0 ? -6 : 1));
    thisMonday.setHours(0, 0, 0, 0);
    setWeekStartDate(thisMonday.toISOString().split('T')[0]);

    const loadData = async () => {
      try {
        // Fetch templates first to get their details
        const templatesData = await scheduleTemplates.getAll();
        
        // Create a map of template IDs to template objects for easy lookup
        const templates: Record<string, WeeklyScheduleTemplateSlot> = {};
        templatesData.forEach((template: WeeklyScheduleTemplateSlot) => {
          templates[template.id] = template;
        });
        setTemplateMap(templates);
        
        // Fetch schedule for the current week
        const scheduleData = await scheduling.getSchedule(thisMonday.toISOString().split('T')[0]);
        
        // Filter rides for the current parent user
        const userRides = scheduleData.filter((ride: RideAssignment) => 
          ride.driver_parent_id === user.id
        );
        setRides(userRides);
      } catch (err) {
        setError('Failed to load your rides. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [user, router]);

  const handleDateChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const newDate = e.target.value;
    setWeekStartDate(newDate);
    setIsLoading(true);
    
    try {
      const scheduleData = await scheduling.getSchedule(newDate);
      
      // Filter rides for the current parent user
      const userRides = scheduleData.filter((ride: RideAssignment) => 
        ride.driver_parent_id === user.id
      );
      setRides(userRides);
    } catch (err) {
      setError('Failed to load schedule for the selected week.');
      setRides([]);
    } finally {
      setIsLoading(false);
    }
  };

  const getDayName = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, { weekday: 'long' });
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const formatTimeRange = (template: WeeklyScheduleTemplateSlot): string => {
    return `${template.start_time} - ${template.end_time}`;
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">My Assigned Rides</h1>
        <p className="mt-1 text-sm text-gray-500">
          View your assigned carpool duties for the selected week.
        </p>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm font-medium text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="space-y-4">
            <div>
              <label htmlFor="week_start_date" className="block text-sm font-medium text-gray-700">
                Week Start Date (Monday)
              </label>
              <input
                type="date"
                id="week_start_date"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={weekStartDate}
                onChange={handleDateChange}
              />
            </div>
          </div>
        </div>
      </div>

      {rides.length === 0 ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-md p-6 text-center">
          <p className="text-gray-500">No rides assigned to you for this week.</p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {rides.map((ride) => {
              const template = templateMap[ride.template_slot_id];
              return (
                <li key={ride.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">
                          {getDayName(ride.assigned_date)}, {formatDate(ride.assigned_date)}
                        </h3>
                        {template && (
                          <>
                            <p className="mt-1 text-sm text-gray-500">
                              Time: {formatTimeRange(template)}
                            </p>
                            <p className="text-sm text-gray-500">
                              Route type: {template.route_type}
                            </p>
                            <p className="text-sm text-gray-500">
                              Max capacity: {template.max_capacity}
                            </p>
                          </>
                        )}
                      </div>
                      <div>
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                          ${ride.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : 
                            ride.status === 'CANCELLED' ? 'bg-red-100 text-red-800' : 
                            'bg-blue-100 text-blue-800'}`}>
                          {ride.status}
                        </span>
                      </div>
                    </div>
                    <div className="mt-2 text-sm text-gray-500">
                      <p>Assignment method: {ride.assignment_method}</p>
                    </div>
                    <div className="mt-2">
                      <a 
                        href={`/dashboard/swap-requests/create?rideId=${ride.id}`}
                        className="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                      >
                        Request Swap
                      </a>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}

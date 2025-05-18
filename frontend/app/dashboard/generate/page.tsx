'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../store/auth';
import { scheduling } from '../../../lib/api';
import { UserRole, RideAssignment } from '../../../types';

export default function GenerateSchedulePage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [weekStartDate, setWeekStartDate] = useState<string>('');
  const [generatedAssignments, setGeneratedAssignments] = useState<RideAssignment[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    // Only admins can access this page
    if (user?.role !== UserRole.ADMIN) {
      router.push('/dashboard');
      return;
    }

    // Calculate next week's Monday as the default week start date
    const today = new Date();
    const nextMonday = new Date(today);
    nextMonday.setDate(today.getDate() + (7 - today.getDay() + 1) % 7 || 7);
    nextMonday.setHours(0, 0, 0, 0);
    setWeekStartDate(nextMonday.toISOString().split('T')[0]);
  }, [user, router]);

  useEffect(() => {
    // Load existing schedule when week start date changes
    if (weekStartDate) {
      loadExistingSchedule();
    }
  }, [weekStartDate]);

  const loadExistingSchedule = async () => {
    if (!weekStartDate) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const schedule = await scheduling.getSchedule(weekStartDate);
      setGeneratedAssignments(schedule);
    } catch (err) {
      // It's ok if there's no schedule yet
      setGeneratedAssignments([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateSchedule = async () => {
    if (!weekStartDate) {
      setError('Please select a valid week start date');
      return;
    }
    
    setIsGenerating(true);
    setError(null);
    
    try {
      const assignments = await scheduling.generateSchedule(weekStartDate);
      setGeneratedAssignments(assignments);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Failed to generate schedule. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setWeekStartDate(e.target.value);
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Generate Schedule</h1>
        <p className="mt-1 text-sm text-gray-500">
          Generate the ride assignments for a specific week based on driver preferences.
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

      {success && (
        <div className="rounded-md bg-green-50 p-4">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800">
                Schedule generated successfully!
              </p>
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
              <p className="mt-1 text-xs text-gray-500">
                Select the Monday that starts the week for which you want to generate a schedule.
              </p>
            </div>
            
            <div className="flex justify-end">
              <button
                onClick={handleGenerateSchedule}
                disabled={isGenerating || isLoading}
                className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {isGenerating ? 'Generating...' : 'Generate Schedule'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-500">Loading...</div>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg font-medium text-gray-900">
              Schedule for week starting {weekStartDate && new Date(weekStartDate).toLocaleDateString()}
            </h3>
          </div>
          
          {generatedAssignments.length === 0 ? (
            <div className="border-t border-gray-200 px-4 py-5 sm:p-6 text-center">
              <p className="text-gray-500">No schedule has been generated for this week yet.</p>
              <p className="mt-1 text-sm text-gray-500">
                Use the form above to generate a schedule based on driver preferences.
              </p>
            </div>
          ) : (
            <div className="border-t border-gray-200">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Driver
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Route
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Assignment Method
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {generatedAssignments.map((assignment) => (
                      <tr key={assignment.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatDate(assignment.assigned_date)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {assignment.driver_parent_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {assignment.template_slot_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            {assignment.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {assignment.assignment_method}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
} 
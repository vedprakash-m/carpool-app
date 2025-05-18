'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '../../../../store/auth';
import { swapRequests, users, scheduling } from '../../../../lib/api';
import { UserRole, User, RideAssignment } from '../../../../types';

export default function CreateSwapRequestPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const rideId = searchParams.get('rideId');
  
  const { user } = useAuthStore();
  const [activeDrivers, setActiveDrivers] = useState<User[]>([]);
  const [selectedDriver, setSelectedDriver] = useState<string>('');
  const [rideDetails, setRideDetails] = useState<RideAssignment | null>(null);
  
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    // Only parents can access this page
    if (user?.role !== UserRole.PARENT) {
      router.push('/dashboard');
      return;
    }

    // If no ride ID is specified, redirect to rides page
    if (!rideId) {
      router.push('/dashboard/rides');
      return;
    }

    const loadData = async () => {
      try {
        // Fetch all active drivers except current user
        const usersData = await users.getAllDrivers();
        const drivers = usersData.filter((driver: User) => 
          driver.id !== user.id && driver.is_active_driver
        );
        setActiveDrivers(drivers);
        
        // If there's a rideId, fetch ride details
        if (rideId) {
          const ride = await scheduling.getRideById(rideId);
          setRideDetails(ride);
          
          // Verify that this ride belongs to the current user
          if (ride.driver_parent_id !== user.id) {
            setError("You can only request swaps for rides assigned to you.");
            setTimeout(() => router.push('/dashboard/rides'), 3000);
          }
        }
      } catch (err) {
        setError('Failed to load data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [user, router, rideId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedDriver) {
      setError('Please select a driver.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    
    try {
      await swapRequests.create(rideId!, selectedDriver);
      setSuccess(true);
      
      // Redirect after success
      setTimeout(() => {
        router.push('/dashboard/swap-requests');
      }, 2000);
    } catch (err) {
      setError('Failed to create swap request. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, { 
      weekday: 'long',
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
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
        <h1 className="text-2xl font-semibold text-gray-900">Request Swap</h1>
        <p className="mt-1 text-sm text-gray-500">
          Request another driver to take your carpool assignment.
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
                Swap request sent successfully! Redirecting...
              </p>
            </div>
          </div>
        </div>
      )}

      {rideDetails && (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Ride Details
            </h3>
          </div>
          <div className="border-t border-gray-200">
            <dl>
              <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Date</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  {formatDate(rideDetails.assigned_date)}
                </dd>
              </div>
              <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                    ${rideDetails.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : 
                      rideDetails.status === 'CANCELLED' ? 'bg-red-100 text-red-800' : 
                      'bg-blue-100 text-blue-800'}`}>
                    {rideDetails.status}
                  </span>
                </dd>
              </div>
              <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Template</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  {rideDetails.template_slot_id}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-6">
            <div>
              <label htmlFor="driver" className="block text-sm font-medium text-gray-700">
                Select Driver to Request Swap
              </label>
              <select
                id="driver"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                value={selectedDriver}
                onChange={(e) => setSelectedDriver(e.target.value)}
                required
              >
                <option value="">-- Select a driver --</option>
                {activeDrivers.map((driver) => (
                  <option key={driver.id} value={driver.id}>
                    {driver.full_name} ({driver.email})
                  </option>
                ))}
              </select>              <p className="mt-2 text-sm text-gray-500 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                This driver will receive an email notification about your swap request.
              </p>
            </div>
          </div>

          <div className="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => router.back()}
              className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !selectedDriver}
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isSubmitting ? 'Sending Request...' : 'Send Request'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '../../store/auth';
import { UserRole } from '../../types';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [greeting, setGreeting] = useState('');

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good morning');
    else if (hour < 18) setGreeting('Good afternoon');
    else setGreeting('Good evening');
  }, []);

  if (!user) return null;

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      <div className="px-4 py-5 sm:px-6">
        <h2 className="text-lg font-medium text-gray-900">
          {greeting}, {user.email}
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Welcome to the Carpool Management App
        </p>
      </div>
      <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
        {user.role === UserRole.ADMIN && (
          <div className="space-y-4">
            <h3 className="text-md font-medium text-gray-900">Admin Quick Links</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                <h4 className="font-medium">Create New User</h4>
                <p className="text-sm text-gray-500">Add a new parent or student to the system</p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                <h4 className="font-medium">Manage Schedule Templates</h4>
                <p className="text-sm text-gray-500">Configure recurring carpool schedule templates</p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                <h4 className="font-medium">Generate Weekly Schedule</h4>
                <p className="text-sm text-gray-500">Create carpool assignments based on preferences</p>
              </div>
            </div>
          </div>
        )}

        {user.role === UserRole.PARENT && (
          <div className="space-y-4">
            <h3 className="text-md font-medium text-gray-900">Parent Quick Links</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                <h4 className="font-medium">Submit Preferences</h4>
                <p className="text-sm text-gray-500">Set your driving preferences for next week</p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                <h4 className="font-medium">View My Rides</h4>
                <p className="text-sm text-gray-500">Check your upcoming driving assignments</p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                <h4 className="font-medium">Swap Requests</h4>
                <p className="text-sm text-gray-500">Manage your ride swap requests</p>
              </div>
            </div>
          </div>
        )}

        {user.role === UserRole.STUDENT && (
          <div className="space-y-4">
            <h3 className="text-md font-medium text-gray-900">Student Dashboard</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                <h4 className="font-medium">View Schedule</h4>
                <p className="text-sm text-gray-500">Check your upcoming carpool schedule</p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                <h4 className="font-medium">Update Profile</h4>
                <p className="text-sm text-gray-500">Update your profile information</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 
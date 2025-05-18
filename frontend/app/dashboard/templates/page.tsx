'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { scheduleTemplates } from '../../../lib/api';
import { useAuthStore } from '../../../store/auth';
import { UserRole, WeeklyScheduleTemplateSlot } from '../../../types';

export default function ScheduleTemplatesPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [templates, setTemplates] = useState<WeeklyScheduleTemplateSlot[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Only admins can access this page
    if (user?.role !== UserRole.ADMIN) {
      router.push('/dashboard');
      return;
    }

    const fetchTemplates = async () => {
      try {
        const data = await scheduleTemplates.getAll();
        setTemplates(data);
      } catch (err) {
        setError('Failed to load schedule templates.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTemplates();
  }, [user, router]);

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this template?')) {
      return;
    }

    try {
      await scheduleTemplates.delete(id);
      setTemplates(templates.filter(template => template.id !== id));
    } catch (err) {
      setError('Failed to delete template.');
    }
  };

  const getDayName = (dayOfWeek: number): string => {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    return days[dayOfWeek];
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
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Schedule Templates</h1>
        <Link
          href="/dashboard/templates/create"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Create New Template
        </Link>
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

      {templates.length === 0 ? (
        <div className="text-center py-12 bg-white shadow rounded-lg">
          <p className="text-gray-500">No schedule templates found.</p>
          <p className="mt-2 text-sm text-gray-500">
            Create a template to define recurring carpool slots.
          </p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {templates.map((template) => (
              <li key={template.id}>
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex flex-col">
                      <p className="text-sm font-medium text-indigo-600 truncate">
                        {getDayName(template.day_of_week)} {template.start_time} - {template.end_time}
                      </p>
                      <p className="mt-1 text-sm text-gray-500">
                        Route type: {template.route_type} · Max capacity: {template.max_capacity}
                      </p>
                    </div>
                    <div className="flex space-x-2">
                      <Link
                        href={`/dashboard/templates/${template.id}`}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200"
                      >
                        Edit
                      </Link>
                      <button
                        onClick={() => handleDelete(template.id)}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
} 
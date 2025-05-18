'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../../store/auth';
import { scheduleTemplates } from '../../../../lib/api';
import { UserRole } from '../../../../types';

interface TemplateFormData {
  day_of_week: number;
  start_time: string;
  end_time: string;
  route_type: string;
  max_capacity: number;
  locations: string;
}

export default function CreateTemplatePage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { register, handleSubmit, formState: { errors } } = useForm<TemplateFormData>({
    defaultValues: {
      day_of_week: 0,
      start_time: '08:00',
      end_time: '09:00',
      route_type: 'SCHOOL_RUN',
      max_capacity: 5,
      locations: ''
    }
  });

  // Redirect if not admin
  if (user?.role !== UserRole.ADMIN) {
    router.push('/dashboard');
    return null;
  }

  const onSubmit = async (data: TemplateFormData) => {
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Convert string locations to array
      const locationsArray = data.locations.split(',').map(location => location.trim());
      
      // Create the template
      await scheduleTemplates.create({
        ...data,
        locations: locationsArray,
        max_capacity: Number(data.max_capacity)
      });
      
      router.push('/dashboard/templates');
    } catch (err) {
      setError('Failed to create template. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg font-medium text-gray-900">Create New Schedule Template</h3>
        
        {error && (
          <div className="mt-4 rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <p className="text-sm font-medium text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}
        
        <form onSubmit={handleSubmit(onSubmit)} className="mt-5 space-y-4">
          <div>
            <label htmlFor="day_of_week" className="block text-sm font-medium text-gray-700">
              Day of Week
            </label>
            <select
              id="day_of_week"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              {...register('day_of_week', { required: 'Day of week is required' })}
            >
              <option value={0}>Monday</option>
              <option value={1}>Tuesday</option>
              <option value={2}>Wednesday</option>
              <option value={3}>Thursday</option>
              <option value={4}>Friday</option>
              <option value={5}>Saturday</option>
              <option value={6}>Sunday</option>
            </select>
            {errors.day_of_week && (
              <p className="mt-1 text-sm text-red-600">{errors.day_of_week.message}</p>
            )}
          </div>
          
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div className="sm:col-span-3">
              <label htmlFor="start_time" className="block text-sm font-medium text-gray-700">
                Start Time
              </label>
              <input
                type="time"
                id="start_time"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                {...register('start_time', { required: 'Start time is required' })}
              />
              {errors.start_time && (
                <p className="mt-1 text-sm text-red-600">{errors.start_time.message}</p>
              )}
            </div>
            
            <div className="sm:col-span-3">
              <label htmlFor="end_time" className="block text-sm font-medium text-gray-700">
                End Time
              </label>
              <input
                type="time"
                id="end_time"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                {...register('end_time', { required: 'End time is required' })}
              />
              {errors.end_time && (
                <p className="mt-1 text-sm text-red-600">{errors.end_time.message}</p>
              )}
            </div>
          </div>
          
          <div>
            <label htmlFor="route_type" className="block text-sm font-medium text-gray-700">
              Route Type
            </label>
            <select
              id="route_type"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              {...register('route_type', { required: 'Route type is required' })}
            >
              <option value="SCHOOL_RUN">School Run (Multi-stop)</option>
              <option value="POINT_TO_POINT">Point-to-Point</option>
            </select>
            {errors.route_type && (
              <p className="mt-1 text-sm text-red-600">{errors.route_type.message}</p>
            )}
          </div>
          
          <div>
            <label htmlFor="max_capacity" className="block text-sm font-medium text-gray-700">
              Maximum Capacity
            </label>
            <input
              type="number"
              id="max_capacity"
              min="1"
              max="10"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              {...register('max_capacity', { 
                required: 'Maximum capacity is required',
                min: {
                  value: 1,
                  message: 'Capacity must be at least 1'
                },
                max: {
                  value: 10,
                  message: 'Capacity cannot exceed 10'
                }
              })}
            />
            {errors.max_capacity && (
              <p className="mt-1 text-sm text-red-600">{errors.max_capacity.message}</p>
            )}
          </div>
          
          <div>
            <label htmlFor="locations" className="block text-sm font-medium text-gray-700">
              Locations (comma-separated)
            </label>
            <textarea
              id="locations"
              rows={3}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Home, School, Park, etc."
              {...register('locations', { required: 'At least one location is required' })}
            ></textarea>
            <p className="mt-1 text-xs text-gray-500">
              Enter location IDs separated by commas. Order matters for the route.
            </p>
            {errors.locations && (
              <p className="mt-1 text-sm text-red-600">{errors.locations.message}</p>
            )}
          </div>
          
          <div className="flex justify-end">
            <button
              type="button"
              onClick={() => router.push('/dashboard/templates')}
              className="mr-3 bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isSubmitting ? 'Creating...' : 'Create Template'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 
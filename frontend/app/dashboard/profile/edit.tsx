'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../store/auth';
import { users } from '../../../lib/api';
import { User } from '../../../types';

interface ProfileUpdateForm {
  full_name: string;
  phone_number?: string;
  home_address?: string;
  is_active_driver?: boolean;
}

export default function EditProfilePage() {
  const router = useRouter();
  const { user, setUser } = useAuthStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  const { register, handleSubmit, formState: { errors }, reset } = useForm<ProfileUpdateForm>();
  
  // Redirect if not authenticated
  if (!user) {
    router.push('/login');
    return null;
  }
  
  // Populate form with current user data
  useEffect(() => {
    if (user) {
      reset({
        full_name: user.full_name,
        phone_number: user.phone_number || '',
        home_address: user.home_address || '',
        is_active_driver: user.is_active_driver
      });
    }
  }, [user, reset]);

  const onSubmit = async (data: ProfileUpdateForm) => {
    setIsSubmitting(true);
    setError(null);
    
    try {
      const updatedUser = await users.updateMe(data);
      setUser(updatedUser);
      setSuccess(true);
      
      // Reset form after success
      setTimeout(() => {
        setSuccess(false);
        router.push('/dashboard/profile');
      }, 2000);
    } catch (err) {
      setError('Failed to update profile. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg font-medium text-gray-900">Edit Your Profile</h3>
        <div className="mt-2 max-w-xl text-sm text-gray-500">
          <p>Update your personal information.</p>
        </div>
        
        {success && (
          <div className="mt-4 rounded-md bg-green-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800">
                  Profile updated successfully! Redirecting...
                </p>
              </div>
            </div>
          </div>
        )}
        
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
            <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
              Full Name
            </label>
            <input
              type="text"
              id="full_name"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              {...register('full_name', { required: 'Full name is required' })}
            />
            {errors.full_name && (
              <p className="mt-1 text-sm text-red-600">{errors.full_name.message}</p>
            )}
          </div>
          
          <div>
            <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700">
              Phone Number
            </label>
            <input
              type="tel"
              id="phone_number"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              {...register('phone_number')}
            />
          </div>
          
          <div>
            <label htmlFor="home_address" className="block text-sm font-medium text-gray-700">
              Home Address
            </label>
            <textarea
              id="home_address"
              rows={3}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              {...register('home_address')}
            ></textarea>
          </div>
          
          {user.role === 'PARENT' && (
            <div className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  id="is_active_driver"
                  type="checkbox"
                  className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                  {...register('is_active_driver')}
                />
              </div>
              <div className="ml-3 text-sm">
                <label htmlFor="is_active_driver" className="font-medium text-gray-700">
                  Active Driver
                </label>
                <p className="text-gray-500">
                  Indicate your availability to be assigned to carpool duties
                </p>
              </div>
            </div>
          )}
          
          <div className="flex justify-end">
            <button
              type="button"
              onClick={() => router.push('/dashboard/profile')}
              className="mr-3 bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../../store/auth';
import { users } from '../../../../lib/api';
import { UserRole } from '../../../../types';

interface CreateUserForm {
  email: string;
  full_name: string;
  role: UserRole;
  initial_password: string;
  confirm_password: string;
  phone_number?: string;
  is_active_driver: boolean;
  home_address?: string;
}

export default function CreateUserPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  const { register, handleSubmit, watch, formState: { errors } } = useForm<CreateUserForm>({
    defaultValues: {
      role: UserRole.PARENT,
      is_active_driver: false
    }
  });
  
  const password = watch('initial_password');
  
  // Redirect if not admin
  if (user?.role !== UserRole.ADMIN) {
    router.push('/dashboard');
    return null;
  }

  const onSubmit = async (data: CreateUserForm) => {
    if (data.initial_password !== data.confirm_password) {
      setError('Passwords do not match');
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      const { confirm_password, ...userData } = data;
      await users.createAdmin(userData);
      setSuccess(true);
      // Reset form or redirect
      setTimeout(() => {
        router.push('/dashboard/users');
      }, 2000);
    } catch (err) {
      setError('Failed to create user. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg font-medium text-gray-900">Create New User</h3>
        
        {success && (
          <div className="mt-4 rounded-md bg-green-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800">
                  User created successfully! Redirecting...
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
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              type="email"
              id="email"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              {...register('email', { 
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address'
                }
              })}
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>
          
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
            <label htmlFor="role" className="block text-sm font-medium text-gray-700">
              Role
            </label>
            <select
              id="role"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              {...register('role', { required: 'Role is required' })}
            >
              <option value={UserRole.PARENT}>Parent</option>
              <option value={UserRole.STUDENT}>Student</option>
            </select>
            {errors.role && (
              <p className="mt-1 text-sm text-red-600">{errors.role.message}</p>
            )}
          </div>
            <div>
            <label htmlFor="initial_password" className="block text-sm font-medium text-gray-700">
              Initial Password
            </label>
            <input
              type="password"
              id="initial_password"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              {...register('initial_password', { 
                required: 'Password is required',
                minLength: {
                  value: 8,
                  message: 'Password must be at least 8 characters'
                },
                validate: {
                  hasUpperCase: value => /[A-Z]/.test(value) || 'Password must contain at least 1 uppercase letter',
                  hasLowerCase: value => /[a-z]/.test(value) || 'Password must contain at least 1 lowercase letter',
                  hasNumber: value => /[0-9]/.test(value) || 'Password must contain at least 1 number',
                  hasSpecialChar: value => /[^A-Za-z0-9]/.test(value) || 'Password must contain at least 1 special character'
                }
              })}
            />
            {errors.initial_password && (
              <p className="mt-1 text-sm text-red-600">{errors.initial_password.message}</p>
            )}
            <div className="mt-1 text-xs text-gray-500">
              Password must be at least 8 characters and include uppercase and lowercase letters, numbers, and special characters.
            </div>
          </div>
          
          <div>
            <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700">
              Confirm Password
            </label>
            <input
              type="password"
              id="confirm_password"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              {...register('confirm_password', { 
                required: 'Please confirm password',
                validate: value => value === password || 'Passwords do not match'
              })}
            />
            {errors.confirm_password && (
              <p className="mt-1 text-sm text-red-600">{errors.confirm_password.message}</p>
            )}
          </div>
          
          <div>
            <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700">
              Phone Number (optional)
            </label>
            <input
              type="tel"
              id="phone_number"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              {...register('phone_number')}
            />
          </div>
          
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
                Designate this parent as an active driver who can be assigned to carpool duties
              </p>
            </div>
          </div>
          
          <div>
            <label htmlFor="home_address" className="block text-sm font-medium text-gray-700">
              Home Address (optional)
            </label>
            <textarea
              id="home_address"
              rows={3}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              {...register('home_address')}
            ></textarea>
          </div>
          
          <div className="flex justify-end">
            <button
              type="button"
              onClick={() => router.push('/dashboard/users')}
              className="mr-3 bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isSubmitting ? 'Creating...' : 'Create User'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 
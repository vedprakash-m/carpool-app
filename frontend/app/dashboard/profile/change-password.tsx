'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../store/auth';
import { users } from '../../../lib/api';

interface PasswordChangeForm {
  current_password: string;
  new_password: string;
  confirm_new_password: string;
}

export default function ChangePasswordPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  const { register, handleSubmit, watch, formState: { errors } } = useForm<PasswordChangeForm>();
  
  const newPassword = watch('new_password');
  
  // Redirect if not authenticated
  if (!user) {
    router.push('/login');
    return null;
  }

  const onSubmit = async (data: PasswordChangeForm) => {
    if (data.new_password !== data.confirm_new_password) {
      setError('Passwords do not match');
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      const { confirm_new_password, ...passwordData } = data;
      await users.changePassword({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      setSuccess(true);
      // Reset form after success
      setTimeout(() => {
        setSuccess(false);
        router.push('/dashboard');
      }, 2000);
    } catch (err) {
      setError('Failed to change password. Please check your current password and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg font-medium text-gray-900">Change Your Password</h3>
        <div className="mt-2 max-w-xl text-sm text-gray-500">
          <p>Update your password to keep your account secure.</p>
        </div>
        
        {success && (
          <div className="mt-4 rounded-md bg-green-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800">
                  Password changed successfully! Redirecting...
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
            <label htmlFor="current_password" className="block text-sm font-medium text-gray-700">
              Current Password
            </label>
            <input
              type="password"
              id="current_password"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              {...register('current_password', { required: 'Current password is required' })}
            />
            {errors.current_password && (
              <p className="mt-1 text-sm text-red-600">{errors.current_password.message}</p>
            )}
          </div>
          
          <div>
            <label htmlFor="new_password" className="block text-sm font-medium text-gray-700">
              New Password
            </label>            <input
              type="password"
              id="new_password"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              {...register('new_password', { 
                required: 'New password is required',
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
            {errors.new_password && (
              <p className="mt-1 text-sm text-red-600">{errors.new_password.message}</p>
            )}
            <div className="mt-2">
              <div className="text-xs text-gray-500 mb-1">Password strength:</div>
              <div className="flex space-x-1">
                <div className={`h-1 w-1/4 rounded ${newPassword?.length >= 8 ? 'bg-green-500' : 'bg-gray-200'}`}></div>
                <div className={`h-1 w-1/4 rounded ${/[A-Z]/.test(newPassword || '') ? 'bg-green-500' : 'bg-gray-200'}`}></div>
                <div className={`h-1 w-1/4 rounded ${/[a-z]/.test(newPassword || '') ? 'bg-green-500' : 'bg-gray-200'}`}></div>
                <div className={`h-1 w-1/4 rounded ${/[0-9]/.test(newPassword || '') ? 'bg-green-500' : 'bg-gray-200'}`}></div>
                <div className={`h-1 w-1/4 rounded ${/[^A-Za-z0-9]/.test(newPassword || '') ? 'bg-green-500' : 'bg-gray-200'}`}></div>
              </div>
              <div className="mt-1 text-xs text-gray-500">
                Password must include: 8+ chars, uppercase, lowercase, number, special character
              </div>
            </div>
          </div>
          
          <div>
            <label htmlFor="confirm_new_password" className="block text-sm font-medium text-gray-700">
              Confirm New Password
            </label>
            <input
              type="password"
              id="confirm_new_password"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              {...register('confirm_new_password', { 
                required: 'Please confirm your new password',
                validate: value => value === newPassword || 'Passwords do not match'
              })}
            />
            {errors.confirm_new_password && (
              <p className="mt-1 text-sm text-red-600">{errors.confirm_new_password.message}</p>
            )}
          </div>
          
          <div className="flex justify-end">
            <button
              type="button"
              onClick={() => router.push('/dashboard')}
              className="mr-3 bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isSubmitting ? 'Changing...' : 'Change Password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

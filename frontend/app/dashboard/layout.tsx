'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '../../store/auth';
import { UserRole } from '../../types';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, token, logout } = useAuthStore();

  useEffect(() => {
    if (!token) {
      router.push('/login');
    }
  }, [token, router]);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-indigo-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-white font-bold">Carpool App</span>
              </div>
              <div className="hidden md:block">
                <div className="ml-10 flex items-baseline space-x-4">
                  <Link
                    href="/dashboard"
                    className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Dashboard
                  </Link>
                  
                  {user.role === UserRole.ADMIN && (
                    <>
                      <Link
                        href="/dashboard/users"
                        className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                      >
                        Users
                      </Link>
                      <Link
                        href="/dashboard/templates"
                        className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                      >
                        Schedule Templates
                      </Link>
                      <Link
                        href="/dashboard/generate"
                        className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                      >
                        Generate Schedule
                      </Link>
                    </>
                  )}
                  
                  {user.role === UserRole.PARENT && (
                    <>
                      <Link
                        href="/dashboard/preferences"
                        className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                      >
                        My Preferences
                      </Link>
                      <Link
                        href="/dashboard/rides"
                        className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                      >
                        My Rides
                      </Link>
                      <Link
                        href="/dashboard/swap-requests"
                        className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                      >
                        Swap Requests
                      </Link>
                    </>
                  )}
                  
                  <Link
                    href="/dashboard/profile"
                    className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Profile
                  </Link>
                </div>
              </div>
            </div>
            <div>
              <button
                onClick={handleLogout}
                className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {children}
        </div>
      </main>
    </div>
  );
} 
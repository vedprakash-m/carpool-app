'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function HomePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    // Detect if we're in a browser environment
    if (typeof window === 'undefined') {
      return;
    }
    
    try {
      console.log('Current pathname:', window.location.pathname);
      
      // Add a slight delay to ensure client-side navigation is ready
      const redirectTimer = setTimeout(() => {
        try {
          // Check if we're already on the login page to prevent redirection loops
          if (window.location.pathname !== '/login') {
            console.log('Redirecting to login page...');
            window.location.href = '/login';
          } else {
            console.log('Already at login page, no redirection needed');
            setIsLoading(false);
          }
        } catch (navError) {
          console.error('Navigation error:', navError);
          setError('Navigation error: ' + (navError instanceof Error ? navError.message : String(navError)));
          setIsLoading(false);
        }
      }, 800);
      
      return () => clearTimeout(redirectTimer);
    } catch (e) {
      console.error('Error in useEffect:', e);
      setError('Error in redirect logic: ' + (e instanceof Error ? e.message : String(e)));
      setIsLoading(false);
    }
  }, [router]);

  if (error) {
    return (
      <div className="min-h-screen flex justify-center items-center">
        <div className="text-center p-4 max-w-md">
          <h2 className="text-2xl font-bold text-red-700">Something went wrong</h2>
          <p className="text-gray-700 mt-2">{error}</p>
          <div className="mt-4">
            <Link href="/login" className="text-blue-600 hover:underline">
              Go to login page manually
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex justify-center items-center">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-700">Welcome to VCarpool</h2>
        <p className="text-gray-500 mt-2">
          {isLoading ? 'Redirecting to login page...' : 'Please wait...'}
        </p>
        {isLoading && (
          <div className="mt-4">
            <p className="text-sm text-gray-500">
              If you are not redirected automatically,{' '}
              <Link href="/login" className="text-blue-600 hover:underline">
                click here
              </Link>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

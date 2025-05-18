'use client';

import React, { useEffect, useState } from 'react';
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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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

  // Navigation links based on user role
  const getNavLinks = () => {
    const links = [{ href: "/dashboard", text: "Dashboard" }];
    
    if (user.role === UserRole.ADMIN) {
      links.push(
        { href: "/dashboard/users", text: "Users" },
        { href: "/dashboard/templates", text: "Schedule Templates" },
        { href: "/dashboard/generate", text: "Generate Schedule" },
        { href: "/dashboard/statistics", text: "Statistics" }
      );
    }
    
    if (user.role === UserRole.PARENT) {
      links.push(
        { href: "/dashboard/preferences", text: "My Preferences" },
        { href: "/dashboard/rides", text: "My Rides" },
        { href: "/dashboard/swap-requests", text: "Swap Requests" }
      );
    }
    
    if (user.role === UserRole.STUDENT) {
      links.push(
        { href: "/dashboard/student/rides", text: "My Rides" }
      );
    }
    
    links.push({ href: "/dashboard/profile", text: "Profile" });
    
    return links;
  };
  
  const navLinks = getNavLinks();

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-indigo-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-white font-bold">Carpool App</span>
              </div>
              {/* Desktop Navigation */}
              <div className="hidden md:block">
                <div className="ml-10 flex items-baseline space-x-4">
                  {navLinks.map((link) => (
                    <Link
                      key={link.href}
                      href={link.href}
                      className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      {link.text}
                    </Link>
                  ))}
                </div>
              </div>
            </div>
            
            {/* Desktop Logout Button */}
            <div className="hidden md:block">
              <button
                onClick={handleLogout}
                className="text-white hover:bg-indigo-500 px-3 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
            
            {/* Mobile menu button */}
            <div className="md:hidden flex items-center">
              <button 
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="inline-flex items-center justify-center p-2 rounded-md text-white hover:bg-indigo-500 focus:outline-none"
              >
                <svg 
                  className={`${mobileMenuOpen ? "hidden" : "block"} h-6 w-6`}
                  xmlns="http://www.w3.org/2000/svg" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor" 
                  aria-hidden="true"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
                <svg 
                  className={`${mobileMenuOpen ? "block" : "hidden"} h-6 w-6`}
                  xmlns="http://www.w3.org/2000/svg" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor" 
                  aria-hidden="true"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        {/* Mobile menu */}
        <div className={`${mobileMenuOpen ? "block" : "hidden"} md:hidden`}>
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-white hover:bg-indigo-500 block px-3 py-2 rounded-md text-base font-medium"
                onClick={() => setMobileMenuOpen(false)}
              >
                {link.text}
              </Link>
            ))}
            <button
              onClick={handleLogout}
              className="text-white hover:bg-indigo-500 block w-full text-left px-3 py-2 rounded-md text-base font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main>
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          {children}
        </div>
      </main>
    </div>
  );
}
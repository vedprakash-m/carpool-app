'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../store/auth';
import { swapRequests } from '../../../lib/api';
import { UserRole, SwapRequest } from '../../../types';

export default function SwapRequestsPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [requests, setRequests] = useState<SwapRequest[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    // Only parents can access this page
    if (user?.role !== UserRole.PARENT) {
      router.push('/dashboard');
      return;
    }

    const loadSwapRequests = async () => {
      try {
        const requestsData = await swapRequests.list();
        setRequests(requestsData);
      } catch (err) {
        setError('Failed to load swap requests. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    loadSwapRequests();
  }, [user, router]);

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const handleAccept = async (requestId: string) => {
    setIsProcessing(prev => ({ ...prev, [requestId]: true }));
    setError(null);
    setSuccess(null);
    
    try {
      await swapRequests.accept(requestId);
      
      // Update the requests list
      setRequests(prev => 
        prev.map(req => 
          req.id === requestId 
            ? { ...req, status: 'ACCEPTED' } 
            : req
        )
      );
      
      setSuccess('Swap request accepted successfully.');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to accept swap request. Please try again.');
    } finally {
      setIsProcessing(prev => ({ ...prev, [requestId]: false }));
    }
  };

  const handleReject = async (requestId: string) => {
    setIsProcessing(prev => ({ ...prev, [requestId]: true }));
    setError(null);
    setSuccess(null);
    
    try {
      await swapRequests.reject(requestId);
      
      // Update the requests list
      setRequests(prev => 
        prev.map(req => 
          req.id === requestId 
            ? { ...req, status: 'REJECTED' } 
            : req
        )
      );
      
      setSuccess('Swap request rejected.');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to reject swap request. Please try again.');
    } finally {
      setIsProcessing(prev => ({ ...prev, [requestId]: false }));
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  const incomingRequests = requests.filter(req => req.requested_driver_id === user?.id);
  const outgoingRequests = requests.filter(req => req.requesting_driver_id === user?.id);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Swap Requests</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your carpool duty swap requests.
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
              <p className="text-sm font-medium text-green-800">{success}</p>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-medium text-gray-900">Incoming Requests</h2>
          <p className="mt-1 text-sm text-gray-500">
            Swap requests from other parents that need your action.
          </p>
        </div>

        {incomingRequests.length === 0 ? (
          <div className="bg-white shadow overflow-hidden sm:rounded-md p-6 text-center">
            <p className="text-gray-500">No incoming swap requests.</p>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {incomingRequests.map((request) => (
                <li key={request.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex justify-between">
                      <div>
                        <p className="text-sm font-medium text-indigo-600">
                          From: {request.requesting_driver_id}
                        </p>
                        <p className="mt-1 text-sm text-gray-500">
                          Ride: {request.ride_assignment_id}
                        </p>
                        <p className="mt-1 text-sm text-gray-500">
                          Requested: {formatDate(request.created_at)}
                        </p>
                      </div>
                      <div>
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                          ${request.status === 'ACCEPTED' ? 'bg-green-100 text-green-800' : 
                            request.status === 'REJECTED' ? 'bg-red-100 text-red-800' : 
                            'bg-yellow-100 text-yellow-800'}`}>
                          {request.status}
                        </span>
                      </div>
                    </div>
                    
                    {request.status === 'PENDING' && (
                      <div className="mt-4 flex space-x-2">                        <button
                          onClick={() => handleAccept(request.id)}
                          disabled={isProcessing[request.id]}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                          title="An email notification will be sent to the requester"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                          {isProcessing[request.id] ? 'Processing...' : 'Accept'}
                        </button>
                        <button
                          onClick={() => handleReject(request.id)}
                          disabled={isProcessing[request.id]}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                          title="An email notification will be sent to the requester"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                          {isProcessing[request.id] ? 'Processing...' : 'Reject'}
                        </button>
                      </div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-8">
          <h2 className="text-lg font-medium text-gray-900">Outgoing Requests</h2>
          <p className="mt-1 text-sm text-gray-500">
            Swap requests you've sent to other parents.
          </p>
        </div>

        {outgoingRequests.length === 0 ? (
          <div className="bg-white shadow overflow-hidden sm:rounded-md p-6 text-center">
            <p className="text-gray-500">No outgoing swap requests.</p>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {outgoingRequests.map((request) => (
                <li key={request.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex justify-between">
                      <div>
                        <p className="text-sm font-medium text-indigo-600">
                          To: {request.requested_driver_id}
                        </p>
                        <p className="mt-1 text-sm text-gray-500">
                          Ride: {request.ride_assignment_id}
                        </p>
                        <p className="mt-1 text-sm text-gray-500">
                          Requested: {formatDate(request.created_at)}
                        </p>
                      </div>
                      <div>
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                          ${request.status === 'ACCEPTED' ? 'bg-green-100 text-green-800' : 
                            request.status === 'REJECTED' ? 'bg-red-100 text-red-800' : 
                            'bg-yellow-100 text-yellow-800'}`}>
                          {request.status}
                        </span>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-4 flex justify-center">
          <button
            onClick={() => router.push('/dashboard/rides')}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            View My Rides
          </button>
        </div>
      </div>
    </div>
  );
}

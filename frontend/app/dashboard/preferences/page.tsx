'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../store/auth';
import { driverPreferences, scheduleTemplates } from '../../../lib/api';
import { UserRole, WeeklyScheduleTemplateSlot, PreferenceLevel } from '../../../types';

export default function DriverPreferencesPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [templates, setTemplates] = useState<WeeklyScheduleTemplateSlot[]>([]);
  const [preferences, setPreferences] = useState<Record<string, PreferenceLevel>>({});
  const [weekStartDate, setWeekStartDate] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    // Only parents can access this page
    if (user?.role !== UserRole.PARENT) {
      router.push('/dashboard');
      return;
    }

    // Calculate next week's Monday as the default week start date
    const today = new Date();
    const nextMonday = new Date(today);
    nextMonday.setDate(today.getDate() + (7 - today.getDay() + 1) % 7 || 7);
    nextMonday.setHours(0, 0, 0, 0);
    setWeekStartDate(nextMonday.toISOString().split('T')[0]);

    const fetchTemplatesAndPreferences = async () => {
      try {
        // Fetch all schedule templates
        const templatesData = await scheduleTemplates.getAll();
        setTemplates(templatesData);
        
        // Try to fetch existing preferences for the selected week
        try {
          const existingPrefs = await driverPreferences.get(nextMonday.toISOString().split('T')[0]);
          
          // Convert array of preferences to a map for easier access
          const prefsMap: Record<string, PreferenceLevel> = {};
          existingPrefs.forEach((pref: any) => {
            prefsMap[pref.template_slot_id] = pref.preference_level;
          });
          
          setPreferences(prefsMap);
        } catch (e) {
          // No preferences exist for this week yet, which is fine
        }
      } catch (err) {
        setError('Failed to load schedule templates or preferences.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTemplatesAndPreferences();
  }, [user, router]);

  const handlePreferenceChange = (templateId: string, level: PreferenceLevel) => {
    // Create a copy of the current preferences
    const updatedPreferences = { ...preferences };
    
    // Check limits for each preference level
    const preferredCount = Object.values(updatedPreferences).filter(p => p === PreferenceLevel.PREFERRED).length;
    const lessPreferredCount = Object.values(updatedPreferences).filter(p => p === PreferenceLevel.LESS_PREFERRED).length;
    const unavailableCount = Object.values(updatedPreferences).filter(p => p === PreferenceLevel.UNAVAILABLE).length;
    
    // If this template already has this preference level, remove it
    if (updatedPreferences[templateId] === level) {
      delete updatedPreferences[templateId];
    } else {
      // Check limits before assigning new preference
      if (level === PreferenceLevel.PREFERRED && preferredCount >= 3 && updatedPreferences[templateId] !== PreferenceLevel.PREFERRED) {
        setError('You can only select up to 3 PREFERRED slots.');
        return;
      }
      
      if (level === PreferenceLevel.LESS_PREFERRED && lessPreferredCount >= 2 && updatedPreferences[templateId] !== PreferenceLevel.LESS_PREFERRED) {
        setError('You can only select up to 2 LESS_PREFERRED slots.');
        return;
      }
      
      if (level === PreferenceLevel.UNAVAILABLE && unavailableCount >= 2 && updatedPreferences[templateId] !== PreferenceLevel.UNAVAILABLE) {
        setError('You can only select up to 2 UNAVAILABLE slots.');
        return;
      }
      
      // Assign the new preference level
      updatedPreferences[templateId] = level;
    }
    
    setPreferences(updatedPreferences);
    setError(null);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Convert preferences map to array for API
      const preferencesArray = Object.entries(preferences).map(([template_slot_id, preference_level]) => ({
        template_slot_id,
        preference_level,
      }));
      
      await driverPreferences.submit(preferencesArray, weekStartDate);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Failed to submit preferences. Please try again.');
    } finally {
      setIsSubmitting(false);
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
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">My Driving Preferences</h1>
        <p className="mt-1 text-sm text-gray-500">
          Set your preferences for the week starting {new Date(weekStartDate).toLocaleDateString()}. 
          You can mark up to 3 slots as preferred, 2 as less preferred, and 2 as unavailable.
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
              <p className="text-sm font-medium text-green-800">
                Preferences submitted successfully!
              </p>
            </div>
          </div>
        </div>
      )}

      {templates.length === 0 ? (
        <div className="text-center py-12 bg-white shadow rounded-lg">
          <p className="text-gray-500">No schedule templates found.</p>
          <p className="mt-2 text-sm text-gray-500">
            Please contact an administrator to create carpool schedule templates.
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
                      <button
                        onClick={() => handlePreferenceChange(template.id, PreferenceLevel.PREFERRED)}
                        className={`px-3 py-1 border text-sm font-medium rounded-md ${
                          preferences[template.id] === PreferenceLevel.PREFERRED
                            ? 'bg-green-600 text-white border-green-600'
                            : 'bg-white text-green-700 border-green-300 hover:bg-green-50'
                        }`}
                      >
                        Preferred
                      </button>
                      <button
                        onClick={() => handlePreferenceChange(template.id, PreferenceLevel.LESS_PREFERRED)}
                        className={`px-3 py-1 border text-sm font-medium rounded-md ${
                          preferences[template.id] === PreferenceLevel.LESS_PREFERRED
                            ? 'bg-yellow-500 text-white border-yellow-500'
                            : 'bg-white text-yellow-700 border-yellow-300 hover:bg-yellow-50'
                        }`}
                      >
                        Less Preferred
                      </button>
                      <button
                        onClick={() => handlePreferenceChange(template.id, PreferenceLevel.UNAVAILABLE)}
                        className={`px-3 py-1 border text-sm font-medium rounded-md ${
                          preferences[template.id] === PreferenceLevel.UNAVAILABLE
                            ? 'bg-red-600 text-white border-red-600'
                            : 'bg-white text-red-700 border-red-300 hover:bg-red-50'
                        }`}
                      >
                        Unavailable
                      </button>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
          
          <div className="px-4 py-4 sm:px-6">
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Preferences'}
            </button>
          </div>
        </div>
      )}
      
      <div className="bg-white p-4 shadow sm:rounded-lg">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Legend</h3>
        <div className="space-y-2">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-600 rounded mr-2"></div>
            <p className="text-sm text-gray-700"><strong>Preferred (Max 3):</strong> Your top choices for driving slots.</p>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-yellow-500 rounded mr-2"></div>
            <p className="text-sm text-gray-700"><strong>Less Preferred (Max 2):</strong> Slots you can drive but prefer not to.</p>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-red-600 rounded mr-2"></div>
            <p className="text-sm text-gray-700"><strong>Unavailable (Max 2):</strong> Slots you cannot drive under any circumstances.</p>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-gray-200 rounded mr-2"></div>
            <p className="text-sm text-gray-700"><strong>Available (Default):</strong> Slots where you're available if needed.</p>
          </div>
        </div>
      </div>
    </div>
  );
} 
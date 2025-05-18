export enum UserRole {
  ADMIN = "ADMIN",
  PARENT = "PARENT",
  STUDENT = "STUDENT"
}

export enum PreferenceLevel {
  PREFERRED = "PREFERRED",
  LESS_PREFERRED = "LESS_PREFERRED",
  UNAVAILABLE = "UNAVAILABLE",
  AVAILABLE_NEUTRAL = "AVAILABLE_NEUTRAL"
}

export enum AssignmentMethod {
  PREFERENCE_BASED = "PREFERENCE_BASED",
  HISTORICAL_BASED = "HISTORICAL_BASED",
  MANUAL = "MANUAL"
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  phone_number?: string;
  is_active_driver: boolean;
  home_address?: string;
  created_at: string;
  updated_at: string;
}

export interface Child {
  id: string;
  parent_id: string;
  full_name: string;
  grade: string;
  school_id: string;
  created_at: string;
  updated_at: string;
}

export interface Location {
  id: string;
  name: string;
  address: string;
  type: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
}

export interface WeeklyScheduleTemplateSlot {
  id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  route_type: string;
  locations: string[];
  max_capacity: number;
  created_at: string;
  updated_at: string;
}

export interface DriverWeeklyPreference {
  id: string;
  driver_parent_id: string;
  week_start_date: string;
  template_slot_id: string;
  preference_level: PreferenceLevel;
  submission_timestamp: string;
}

export interface RideAssignment {
  id: string;
  template_slot_id: string;
  driver_parent_id: string;
  assigned_date: string;
  status: string;
  assignment_method: AssignmentMethod;
  created_at: string;
  updated_at: string;
}

export interface SwapRequest {
  id: string;
  requesting_driver_id: string;
  requested_driver_id: string;
  ride_assignment_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  role: UserRole;
} 
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import uuid

from app.db.cosmos import get_container
from app.models.core import PreferenceLevel, AssignmentMethod


class ScheduleGenerator:
    """
    Service for generating weekly ride schedules based on driver preferences
    and historical assignments for fair distribution.
    """
    
    def __init__(self, week_start_date: date):
        """Initialize with the week's start date (should be a Monday)"""
        self.week_start_date = week_start_date
        
        # Init container clients
        self.templates_container = get_container("weekly_schedule_template_slots")
        self.prefs_container = get_container("driver_weekly_preferences")
        self.assignments_container = get_container("ride_assignments")
        self.users_container = get_container("users")
    
    def _get_template_slots(self) -> List[Dict]:
        """Get all weekly schedule template slots"""
        query = "SELECT * FROM c"
        return list(self.templates_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
    
    def _get_active_drivers(self) -> List[Dict]:
        """Get all active drivers from the system"""
        query = "SELECT * FROM c WHERE c.is_active_driver = true"
        return list(self.users_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
    
    def _get_driver_preferences(self, driver_id: str) -> Dict[str, str]:
        """Get preferences for a specific driver for the week"""
        query = """
        SELECT * FROM c 
        WHERE c.driver_parent_id = @driver_id
        AND c.week_start_date = @week_start_date
        """
        params = [
            {"name": "@driver_id", "value": driver_id},
            {"name": "@week_start_date", "value": self.week_start_date.isoformat()}
        ]
        
        prefs = list(self.prefs_container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        
        # Transform into a dict of slot_id -> preference_level
        return {p["template_slot_id"]: p["preference_level"] for p in prefs}
    
    def _get_historical_assignments(self, lookback_weeks: int = 4) -> Dict[str, int]:
        """
        Get historical driver assignments for the past N weeks
        Returns a dict of driver_id -> count of assignments
        """
        oldest_date = (self.week_start_date - timedelta(days=7*lookback_weeks)).isoformat()
        
        query = """
        SELECT c.driver_parent_id, COUNT(1) as assignment_count
        FROM c
        WHERE c.assigned_date >= @oldest_date
        GROUP BY c.driver_parent_id
        """
        params = [{"name": "@oldest_date", "value": oldest_date}]
        
        results = self.assignments_container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        )
        
        return {r["driver_parent_id"]: r["assignment_count"] for r in results}
    
    def generate_schedule(self) -> List[Dict]:
        """
        Generate a schedule for the week based on driver preferences
        and historical assignments.
        
        Algorithm:
        1. Get all template slots and active drivers
        2. For each day in the week:
           - For each slot that day:
             a. Exclude drivers who marked this slot as UNAVAILABLE
             b. Prioritize drivers with PREFERRED status
             c. If no PREFERRED drivers, try LESS_PREFERRED
             d. If no preferences, use drivers with AVAILABLE_NEUTRAL
             e. If still no assignment, use historical data to pick the driver
                with fewest recent assignments
        """
        slots = self._get_template_slots()
        drivers = self._get_active_drivers()
        
        # Get all driver preferences for the week
        all_preferences = {}
        for driver in drivers:
            all_preferences[driver["id"]] = self._get_driver_preferences(driver["id"])
        
        # Get historical assignment counts
        historical_counts = self._get_historical_assignments()
        
        # Default to 0 for drivers with no historical assignments
        for driver in drivers:
            if driver["id"] not in historical_counts:
                historical_counts[driver["id"]] = 0
        
        assignments = []
        
        # Group slots by day
        slots_by_day = {}
        for slot in slots:
            day = slot["day_of_week"]
            if day not in slots_by_day:
                slots_by_day[day] = []
            slots_by_day[day].append(slot)
        
        # Generate assignments for each day
        for day_offset in range(7):  # 0 = Monday, 6 = Sunday
            day_date = self.week_start_date + timedelta(days=day_offset)
            day_slots = slots_by_day.get(day_offset, [])
            
            for slot in day_slots:
                assignment = self._assign_driver_to_slot(
                    slot, 
                    drivers, 
                    all_preferences, 
                    historical_counts,
                    day_date
                )
                
                if assignment:
                    # Update historical counts for fairness in subsequent assignments
                    historical_counts[assignment["driver_parent_id"]] += 1
                    assignments.append(assignment)
        
        # Batch create the assignments
        for assignment in assignments:
            self.assignments_container.create_item(body=assignment)
            
        return assignments
    
    def _assign_driver_to_slot(
        self, 
        slot: Dict, 
        drivers: List[Dict],
        all_preferences: Dict[str, Dict[str, str]],
        historical_counts: Dict[str, int],
        assignment_date: date
    ) -> Optional[Dict]:
        """
        Assign a driver to a specific slot based on preferences and history.
        Returns the assignment data or None if no assignment could be made.
        """
        slot_id = slot["id"]
        
        # Step 1: Filter out UNAVAILABLE drivers
        available_drivers = [d for d in drivers if 
                            all_preferences.get(d["id"], {}).get(slot_id) != PreferenceLevel.UNAVAILABLE]
        
        if not available_drivers:
            # Nobody available for this slot
            return None
        
        # Step 2: Try to find PREFERRED drivers
        preferred_drivers = [d for d in available_drivers if 
                           all_preferences.get(d["id"], {}).get(slot_id) == PreferenceLevel.PREFERRED]
        
        # Step 3: If no PREFERRED, try LESS_PREFERRED
        if not preferred_drivers:
            preferred_drivers = [d for d in available_drivers if 
                               all_preferences.get(d["id"], {}).get(slot_id) == PreferenceLevel.LESS_PREFERRED]
        
        # Step 4: If still no match, use AVAILABLE_NEUTRAL
        if not preferred_drivers:
            preferred_drivers = [d for d in available_drivers]
        
        # Step 5: Use historical data for final selection or tie-breaking
        if preferred_drivers:
            # Sort by least historical assignments
            selected_driver = sorted(
                preferred_drivers, 
                key=lambda d: historical_counts.get(d["id"], 0)
            )[0]
            
            assignment_method = AssignmentMethod.PREFERENCE_BASED
            if all_preferences.get(selected_driver["id"], {}).get(slot_id) is None:
                # No explicit preference was set, using historical data
                assignment_method = AssignmentMethod.HISTORICAL_BASED
            
            # Create assignment
            return {
                "id": str(uuid.uuid4()),
                "template_slot_id": slot_id,
                "driver_parent_id": selected_driver["id"],
                "assigned_date": assignment_date.isoformat(),
                "status": "SCHEDULED",
                "assignment_method": assignment_method,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        
        return None

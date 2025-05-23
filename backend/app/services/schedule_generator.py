from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import uuid
import logging

from app.db.cosmos import get_container
from app.models.core import PreferenceLevel, AssignmentMethod

# Configure logging
logger = logging.getLogger(__name__)

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
        try:
            query = "SELECT * FROM c"
            return list(self.templates_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
        except Exception as e:
            logger.error(f"Failed to get template slots: {str(e)}")
            raise
    
    def _get_active_drivers(self) -> List[Dict]:
        """Get all active drivers from the system"""
        try:
            query = "SELECT * FROM c WHERE c.is_active_driver = true"
            return list(self.users_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
        except Exception as e:
            logger.error(f"Failed to get active drivers: {str(e)}")
            raise
    
    def _get_driver_preferences(self, driver_id: str) -> Dict[str, str]:
        """Get preferences for a specific driver for the week"""
        try:
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
        except Exception as e:
            logger.error(f"Failed to get driver preferences for {driver_id}: {str(e)}")
            return {}
    
    def _get_historical_assignments(self, lookback_weeks: int = 4) -> Dict[str, Dict]:
        """
        Get historical driver assignments for the past N weeks
        Returns a dict with driver_id -> {
            'count': total assignments,
            'weighted_count': weighted by recency,
            'last_assignment_date': date of most recent assignment
        }
        """
        try:
            oldest_date = (self.week_start_date - timedelta(days=7*lookback_weeks)).isoformat()
            
            query = """
            SELECT c.driver_parent_id, c.assigned_date
            FROM c
            WHERE c.assigned_date >= @oldest_date
            AND c.assigned_date < @current_week
            """
            params = [
                {"name": "@oldest_date", "value": oldest_date},
                {"name": "@current_week", "value": self.week_start_date.isoformat()}
            ]
            
            results = list(self.assignments_container.query_items(
                query=query,
                parameters=params,
                enable_cross_partition_query=True
            ))
            
            # Group by driver and calculate metrics
            driver_metrics = {}
            
            for r in results:
                driver_id = r["driver_parent_id"]
                assign_date = date.fromisoformat(r["assigned_date"])
                days_ago = (self.week_start_date - assign_date).days
                
                # Weighted count gives more weight to recent assignments
                # 1.0 for this week, 0.75 for last week, 0.5 for 2 weeks ago, 0.25 for 3 weeks ago
                recency_weight = max(0, 1.0 - (days_ago / (lookback_weeks * 7 * 1.5)))
                
                if driver_id not in driver_metrics:
                    driver_metrics[driver_id] = {
                        'count': 0,
                        'weighted_count': 0,
                        'last_assignment_date': None
                    }
                
                driver_metrics[driver_id]['count'] += 1
                driver_metrics[driver_id]['weighted_count'] += recency_weight
                
                # Update most recent assignment date
                if driver_metrics[driver_id]['last_assignment_date'] is None or assign_date > driver_metrics[driver_id]['last_assignment_date']:
                    driver_metrics[driver_id]['last_assignment_date'] = assign_date
            
            return driver_metrics
        except Exception as e:
            logger.error(f"Failed to get historical assignments: {str(e)}")
            return {}
    
    def _clear_existing_assignments(self) -> None:
        """Clear any existing assignments for the target week"""
        try:
            week_end_date = (self.week_start_date + timedelta(days=7)).isoformat()
            
            query = """
            SELECT * FROM c 
            WHERE c.assigned_date >= @start_date 
            AND c.assigned_date < @end_date
            """
            params = [
                {"name": "@start_date", "value": self.week_start_date.isoformat()},
                {"name": "@end_date", "value": week_end_date}
            ]
            
            existing_assignments = list(self.assignments_container.query_items(
                query=query,
                parameters=params,
                enable_cross_partition_query=True
            ))
            
            # Delete existing assignments
            for assignment in existing_assignments:
                self.assignments_container.delete_item(
                    item=assignment["id"],
                    partition_key=assignment["driver_parent_id"]
                )
                
            logger.info(f"Cleared {len(existing_assignments)} existing assignments for week of {self.week_start_date.isoformat()}")
        except Exception as e:
            logger.error(f"Failed to clear existing assignments: {str(e)}")
            raise
    
    def get_existing_assignments(self) -> List[Dict]:
        """
        Get existing ride assignments for the current week
        Returns a list of assignment data
        """
        try:
            week_end_date = (self.week_start_date + timedelta(days=7)).isoformat()
            
            query = """
            SELECT * FROM c 
            WHERE c.assigned_date >= @start_date 
            AND c.assigned_date < @end_date
            """
            params = [
                {"name": "@start_date", "value": self.week_start_date.isoformat()},
                {"name": "@end_date", "value": week_end_date}
            ]
            
            assignments = list(self.assignments_container.query_items(
                query=query,
                parameters=params,
                enable_cross_partition_query=True
            ))
            
            logger.info(f"Retrieved {len(assignments)} assignments for week of {self.week_start_date.isoformat()}")
            return assignments
            
        except Exception as e:
            logger.error(f"Failed to get existing assignments: {str(e)}")
            return []
    
    def generate_schedule(self, clear_existing: bool = True) -> List[Dict]:
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
        try:
            logger.info(f"Generating schedule for week of {self.week_start_date.isoformat()}")
            
            # Clear existing assignments if requested
            if clear_existing:
                self._clear_existing_assignments()
            
            slots = self._get_template_slots()
            drivers = self._get_active_drivers()
            
            if not drivers:
                logger.warning("No active drivers found, cannot generate schedule")
                return []
                
            if not slots:
                logger.warning("No schedule template slots found, cannot generate schedule")
                return []
            
            # Get all driver preferences for the week
            all_preferences = {}
            for driver in drivers:
                all_preferences[driver["id"]] = self._get_driver_preferences(driver["id"])
            
            # Get historical assignment data
            historical_data = self._get_historical_assignments()
            
            # Prepare summary metrics for all drivers
            driver_metrics = {}
            for driver in drivers:
                driver_id = driver["id"]
                if driver_id in historical_data:
                    driver_metrics[driver_id] = historical_data[driver_id]
                else:
                    driver_metrics[driver_id] = {
                        'count': 0,
                        'weighted_count': 0,
                        'last_assignment_date': None
                    }
            
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
                        driver_metrics,
                        day_date
                    )
                    
                    if assignment:
                        # Update metrics for fairness in subsequent assignments
                        driver_id = assignment["driver_parent_id"]
                        driver_metrics[driver_id]['count'] += 1
                        driver_metrics[driver_id]['weighted_count'] += 1.0  # Full weight for new assignment
                        driver_metrics[driver_id]['last_assignment_date'] = day_date
                        assignments.append(assignment)
            
            # Batch create the assignments
            for assignment in assignments:
                self.assignments_container.create_item(body=assignment)
                
            logger.info(f"Successfully generated {len(assignments)} assignments for week of {self.week_start_date.isoformat()}")
            return assignments
            
        except Exception as e:
            logger.error(f"Failed to generate schedule: {str(e)}")
            raise
    
    def _assign_driver_to_slot(
        self, 
        slot: Dict, 
        drivers: List[Dict],
        all_preferences: Dict[str, Dict[str, str]],
        driver_metrics: Dict[str, Dict],
        assignment_date: date
    ) -> Optional[Dict]:
        """
        Assign a driver to a specific slot based on preferences and history.
        Returns the assignment data or None if no assignment could be made.
        
        Enhanced to consider:
        - Recent assignment weight (more recent = higher weight)
        - Time since last assignment
        - Overall historical fairness
        """
        try:
            slot_id = slot["id"]
            
            # Step 1: Filter out UNAVAILABLE drivers
            available_drivers = [d for d in drivers if 
                               all_preferences.get(d["id"], {}).get(slot_id) != PreferenceLevel.UNAVAILABLE]
            
            if not available_drivers:
                logger.warning(f"No available drivers for slot {slot_id} on {assignment_date.isoformat()}")
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
                preferred_drivers = available_drivers
            
            # Step 5: Use enhanced metrics for final selection
            if preferred_drivers:
                # Sort by a combination of factors:
                # 1. Weighted historical count (lower is better)
                # 2. Days since last assignment (higher is better)
                # 3. Total assignment count (lower is better)
                def get_driver_score(driver):
                    d_id = driver["id"]
                    metrics = driver_metrics[d_id]
                    
                    # Base score from weighted historical count
                    score = -1 * metrics['weighted_count'] * 10
                    
                    # Add bonus for not being assigned recently
                    if metrics['last_assignment_date'] is None:
                        # Big bonus for never assigned
                        score += 50
                    else:
                        days_since_last = (assignment_date - metrics['last_assignment_date']).days
                        score += min(30, days_since_last)  # Cap at 30 days
                    
                    # Small penalty for total count
                    score -= metrics['count']
                    
                    return score
                
                # Select driver with best score
                selected_driver = sorted(
                    preferred_drivers, 
                    key=get_driver_score,
                    reverse=True  # Higher score is better
                )[0]
                
                # Determine assignment method
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
                
            logger.warning(f"Could not assign a driver for slot {slot_id} on {assignment_date.isoformat()}")
            return None
            
        except Exception as e:
            logger.error(f"Error assigning driver to slot {slot['id']}: {str(e)}")
            return None

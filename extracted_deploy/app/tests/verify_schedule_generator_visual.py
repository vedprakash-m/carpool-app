"""
Simple scheduler verification script with better output and visualization
"""
import sys
import os
from datetime import date, timedelta
from tabulate import tabulate
from colorama import init, Fore, Style
from unittest.mock import patch, MagicMock

# Initialize colorama
init()

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

print(f"{Fore.CYAN}Schedule Generator Verification{Style.RESET_ALL}")
print(f"{Fore.CYAN}=============================\n{Style.RESET_ALL}")

# Mock the settings
with patch('app.core.config.get_settings') as mock_get_settings:
    # Create mock settings
    mock_settings = MagicMock()
    mock_settings.COSMOS_ENDPOINT = "https://mock-cosmos.azure.com:443/"
    mock_settings.COSMOS_KEY = "mock-key=="
    mock_settings.COSMOS_DATABASE = "carpool_db_test"
    mock_settings.JWT_SECRET_KEY = "mock-jwt-key"
    mock_settings.JWT_ALGORITHM = "HS256"
    mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60
    
    mock_get_settings.return_value = mock_settings
    
    # Import the app modules after patching settings
    from app.models.core import PreferenceLevel, AssignmentMethod
    
    # Mock the cosmos client
    with patch('app.db.cosmos.get_container') as mock_get_container:
        # Create mock container
        mock_container = MagicMock()
        
        # Set up template slots mock data
        template_slots = [
            {
                "id": "slot1",
                "day_of_week": 0,  # Monday
                "time_slot": "MORNING",
                "display_name": "Monday Morning"
            },
            {
                "id": "slot2",
                "day_of_week": 0,  # Monday
                "time_slot": "AFTERNOON", 
                "display_name": "Monday Afternoon"
            },
            {
                "id": "slot3",
                "day_of_week": 1,  # Tuesday
                "time_slot": "MORNING",
                "display_name": "Tuesday Morning"
            },
            {
                "id": "slot4",
                "day_of_week": 1,  # Tuesday
                "time_slot": "AFTERNOON",
                "display_name": "Tuesday Afternoon"
            }
        ]
        
        drivers = [
            {
                "id": "driver1",
                "name": "Alice Smith",
                "is_active_driver": True
            },
            {
                "id": "driver2", 
                "name": "Bob Johnson",
                "is_active_driver": True
            },
            {
                "id": "driver3",
                "name": "Carol Davis",
                "is_active_driver": True
            }
        ]
        
        # Mock preferences data
        week_start = date(2025, 5, 26)  # A Monday
        prefs = [
            # Driver 1 preferences
            {
                "id": "pref1",
                "driver_parent_id": "driver1",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot1",
                "preference_level": PreferenceLevel.PREFERRED
            },
            {
                "id": "pref2",
                "driver_parent_id": "driver1",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot2",
                "preference_level": PreferenceLevel.LESS_PREFERRED
            },
            {
                "id": "pref3",
                "driver_parent_id": "driver1",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot3",
                "preference_level": PreferenceLevel.UNAVAILABLE
            },
            {
                "id": "pref4",
                "driver_parent_id": "driver1",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot4",
                "preference_level": PreferenceLevel.AVAILABLE_NEUTRAL
            },
            
            # Driver 2 preferences
            {
                "id": "pref5",
                "driver_parent_id": "driver2",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot1",
                "preference_level": PreferenceLevel.LESS_PREFERRED
            },
            {
                "id": "pref6", 
                "driver_parent_id": "driver2",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot2",
                "preference_level": PreferenceLevel.PREFERRED
            },
            {
                "id": "pref7",
                "driver_parent_id": "driver2",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot3",
                "preference_level": PreferenceLevel.PREFERRED
            },
            {
                "id": "pref8",
                "driver_parent_id": "driver2",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot4",
                "preference_level": PreferenceLevel.UNAVAILABLE
            },
            
            # Driver 3 preferences
            {
                "id": "pref9",
                "driver_parent_id": "driver3",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot1",
                "preference_level": PreferenceLevel.UNAVAILABLE
            },
            {
                "id": "pref10",
                "driver_parent_id": "driver3",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot2",
                "preference_level": PreferenceLevel.UNAVAILABLE
            },
            {
                "id": "pref11",
                "driver_parent_id": "driver3",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot3",
                "preference_level": PreferenceLevel.LESS_PREFERRED
            },
            {
                "id": "pref12",
                "driver_parent_id": "driver3", 
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot4",
                "preference_level": PreferenceLevel.PREFERRED
            }
        ]
        
        # Historical assignments for fairness
        history = [
            {
                "id": "hist1",
                "driver_parent_id": "driver1",
                "assigned_date": (week_start - timedelta(days=7)).isoformat()
            },
            {
                "id": "hist2",
                "driver_parent_id": "driver1",
                "assigned_date": (week_start - timedelta(days=14)).isoformat()
            },
            {
                "id": "hist3",
                "driver_parent_id": "driver2",
                "assigned_date": (week_start - timedelta(days=21)).isoformat()
            }
        ]
        
        # Set up query_items side effect
        def mock_query_items(**kwargs):
            query = kwargs.get("query", "")
            parameters = kwargs.get("parameters", [])
            
            # Return template slots
            if "SELECT * FROM c" in query and "WHERE" not in query:
                return template_slots
            
            # Return active drivers
            elif "is_active_driver = true" in query:
                return drivers
            
            # Return preferences
            elif "driver_parent_id" in query and "week_start_date" in query:
                driver_id = next((p["value"] for p in parameters if p["name"] == "@driver_id"), None)
                return [p for p in prefs if p["driver_parent_id"] == driver_id]
            
            # Return historical assignments
            elif "assigned_date >=" in query:
                return history
            
            # Default empty list
            return []
        
        # Store created assignments
        created_assignments = []
        def mock_create_item(body):
            created_assignments.append(body)
            return body
        
        # Set up mock container
        mock_container.query_items = mock_query_items
        mock_container.create_item = mock_create_item
        mock_get_container.return_value = mock_container
        
        # Now import and test the ScheduleGenerator
        from app.services.schedule_generator import ScheduleGenerator
        
        # Create a test instance
        generator = ScheduleGenerator(week_start)
        
        # Test the algorithm
        print(f"{Fore.GREEN}Generating schedule for week starting {week_start}{Style.RESET_ALL}\n")
        
        # Print driver preferences in tabular format
        print(f"{Fore.YELLOW}Driver Preferences:{Style.RESET_ALL}")
        
        # Create preference table
        pref_table = []
        for driver in drivers:
            driver_prefs = {}
            for slot in template_slots:
                slot_id = slot["id"]
                pref = next((p for p in prefs if p["driver_parent_id"] == driver["id"] and p["template_slot_id"] == slot_id), None)
                if pref:
                    if pref["preference_level"] == PreferenceLevel.PREFERRED:
                        driver_prefs[slot["display_name"]] = f"{Fore.GREEN}PREFERRED{Style.RESET_ALL}"
                    elif pref["preference_level"] == PreferenceLevel.LESS_PREFERRED:
                        driver_prefs[slot["display_name"]] = f"{Fore.YELLOW}LESS_PREFERRED{Style.RESET_ALL}"
                    elif pref["preference_level"] == PreferenceLevel.UNAVAILABLE:
                        driver_prefs[slot["display_name"]] = f"{Fore.RED}UNAVAILABLE{Style.RESET_ALL}"
                    else:
                        driver_prefs[slot["display_name"]] = f"{Fore.BLUE}NEUTRAL{Style.RESET_ALL}"
                else:
                    driver_prefs[slot["display_name"]] = ""
            
            pref_row = {"Driver": driver["name"]}
            pref_row.update(driver_prefs)
            pref_table.append(pref_row)
        
        print(tabulate(pref_table, headers="keys", tablefmt="pretty"))
        print()
        
        # Print historical assignments
        print(f"{Fore.YELLOW}Historical Assignment Counts:{Style.RESET_ALL}")
        driver_counts = {}
        for hist in history:
            driver_id = hist["driver_parent_id"]
            driver_name = next((d["name"] for d in drivers if d["id"] == driver_id), "Unknown")
            if driver_name not in driver_counts:
                driver_counts[driver_name] = 0
            driver_counts[driver_name] += 1
        
        for driver in drivers:
            if driver["name"] not in driver_counts:
                driver_counts[driver["name"]] = 0
        
        history_table = [{"Driver": name, "Assignments": count} for name, count in driver_counts.items()]
        print(tabulate(history_table, headers="keys", tablefmt="pretty"))
        print()
        
        # Generate the schedule
        print(f"{Fore.CYAN}Generating schedule...{Style.RESET_ALL}")
        try:
            assignments = generator.generate_schedule()
            print(f"{Fore.GREEN}Successfully generated {len(assignments)} assignments!{Style.RESET_ALL}\n")
            
            # Create results table
            results_table = []
            for slot in template_slots:
                slot_id = slot["id"]
                assignment = next((a for a in assignments if a["template_slot_id"] == slot_id), None)
                
                if assignment:
                    driver_id = assignment["driver_parent_id"]
                    driver_name = next((d["name"] for d in drivers if d["id"] == driver_id), "Unknown")
                    method = assignment["assignment_method"]
                    
                    if method == AssignmentMethod.PREFERENCE_BASED:
                        method_display = f"{Fore.GREEN}{method}{Style.RESET_ALL}"
                    else:
                        method_display = f"{Fore.BLUE}{method}{Style.RESET_ALL}"
                    
                    results_table.append({
                        "Slot": slot["display_name"],
                        "Assigned Driver": driver_name,
                        "Assignment Method": method_display
                    })
                else:
                    results_table.append({
                        "Slot": slot["display_name"],
                        "Assigned Driver": f"{Fore.RED}No Assignment{Style.RESET_ALL}",
                        "Assignment Method": ""
                    })
            
            print(f"{Fore.YELLOW}Generated Schedule:{Style.RESET_ALL}")
            print(tabulate(results_table, headers="keys", tablefmt="pretty"))
            print()
            
            # Verify expectations
            all_slots_covered = all(any(a["template_slot_id"] == slot["id"] for a in assignments) for slot in template_slots if any(p["template_slot_id"] == slot["id"] and p["preference_level"] != PreferenceLevel.UNAVAILABLE for p in prefs))
            
            if all_slots_covered:
                print(f"{Fore.GREEN}✓ All slots with available drivers were assigned{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ Some slots with available drivers were not assigned{Style.RESET_ALL}")
            
            # Verify preferences were respected
            prefs_respected = True
            for assignment in assignments:
                slot_id = assignment["template_slot_id"]
                driver_id = assignment["driver_parent_id"]
                driver_prefs = [p for p in prefs if p["driver_parent_id"] == driver_id and p["template_slot_id"] == slot_id]
                
                if driver_prefs and driver_prefs[0]["preference_level"] == PreferenceLevel.UNAVAILABLE:
                    prefs_respected = False
                    break
            
            if prefs_respected:
                print(f"{Fore.GREEN}✓ All driver unavailability preferences were respected{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ Some drivers were assigned to slots they marked as unavailable{Style.RESET_ALL}")
            
            # Verify fairness
            driver_assignment_counts = {}
            for assignment in assignments:
                driver_id = assignment["driver_parent_id"]
                driver_name = next((d["name"] for d in drivers if d["id"] == driver_id), "Unknown")
                if driver_name not in driver_assignment_counts:
                    driver_assignment_counts[driver_name] = 0
                driver_assignment_counts[driver_name] += 1
            
            for driver in drivers:
                if driver["name"] not in driver_assignment_counts:
                    driver_assignment_counts[driver["name"]] = 0
            
            max_count = max(driver_assignment_counts.values()) if driver_assignment_counts else 0
            min_count = min(driver_assignment_counts.values()) if driver_assignment_counts else 0
            
            if max_count - min_count <= 1:
                print(f"{Fore.GREEN}✓ Assignments are fairly distributed (max difference of 1 assignment){Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠ Assignment distribution could be improved (difference of {max_count - min_count} assignments){Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}Schedule verification complete!{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}Error generating schedule: {str(e)}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()

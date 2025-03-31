from datetime import datetime, timedelta
from .bee import Bee
import os
from dotenv import load_dotenv
from .beemcp import resource_get_todo, create_todo, update_todo, delete_todo, mark_todo_completed, resource_list_incomplete_todos, resource_get_fact, resource_list_facts, resource_list_conversations, confirm_fact, get_fact, delete_fact, create_fact, resource_get_conversation, resource_get_fact, resource_list_facts, resource_list_conversations, list_all_locations, get_locations_time_range, resource_locations_today, resource_locations_week

# Load environment variables from .env file
load_dotenv()

# Get API token from environment variables
api_token = os.getenv("BEE_API_TOKEN")
if not api_token:
    raise ValueError("BEE_API_TOKEN environment variable is not set")

# Initialize Bee with API token
bee = Bee(api_token)



if __name__ == '__main__':
    print("=== TESTING CONVERSATIONS ===")
    conversations = resource_list_conversations()
    for conversation in conversations:
        if len(conversation) > 200:
            print(conversation[:200] + "...")
        else:
            print(conversation)
    conversation_id = input("Enter the id of the conversation to get (or press Enter to skip): ")
    if conversation_id:
        print(resource_get_conversation(conversation_id))
    
    print("=== TESTING FACTS ===")
    facts = resource_list_facts()
    for fact in facts:
        print(fact)
    fact_id = input("Enter the id of the fact to get (or press Enter to skip): ")
    if fact_id:
        print(resource_get_fact(fact_id))
        print("We will make that fact into a suggestion, so you can go back in the Bee app and approve it again.")
        print(confirm_fact(fact_id, False))
        print(get_fact(fact_id))
    new_fact = input("Type a new fact to create (or press Enter to skip): ")
    if new_fact:
        print(create_fact(new_fact))
    
    print("=== TESTING TODOS ===")
    todos = resource_list_incomplete_todos()
    for todo in todos:
        print(todo)
    todo_id = input("Enter the id of the todo to update/delete (or press Enter to skip): ")
    if todo_id:
        print(resource_get_todo(todo_id))
        # Set alarm time to one hour from now
        one_hour_from_now = datetime.now() + timedelta(hours=1)
        print(update_todo(todo_id, alarm_at=one_hour_from_now.isoformat()))
        print(resource_get_todo(todo_id))
        print(mark_todo_completed(todo_id))
        print(delete_todo(todo_id))
    
    print("=== TESTING LOCATIONS ===")
    
    # Test listing all locations
    print("All locations:")
    all_locations = list_all_locations()
    for location in all_locations[:5]:  # Show first 5 to avoid overwhelming output
        print(location)
    print(f"Total locations: {len(all_locations)}")
    
    # Test locations from today
    print("\nLocations from today:")
    today_locations = resource_locations_today()
    for location in today_locations:
        print(location)
    print(f"Total today locations: {len(today_locations)}")
    
    # Test locations from this week
    print("\nLocations from this week:")
    week_locations = resource_locations_week()
    print(f"Total week locations: {len(week_locations)}")
    for location in week_locations[:5]:  # Show first 5 to avoid overwhelming output
        print(location)
    
    # Test custom date range
    print("\nTesting custom date range:")
    # Set date range to last 3 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    
    # Format dates as ISO strings
    start_iso = start_date.isoformat()
    end_iso = end_date.isoformat()
    
    print(f"Locations from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}:")
    custom_locations = get_locations_time_range(start_time=start_iso, end_time=end_iso)
    print(f"Total custom range locations: {len(custom_locations)}")
    for location in custom_locations[:5]:  # Show first 5 to avoid overwhelming output
        print(location)
    
    # Get a specific location if available
    all_locations = bee.list_all_locations()
    location_id = input("Enter the ID of a location to view details (or press Enter to skip): ")
    if location_id:
        # Find the location with the given ID
        for location in all_locations:
            if str(location.id) == location_id:
                print(location.get_llm_text())
                break
        else:
            print(f"Location with ID {location_id} not found")
    
    print("=== COMPLETE ===")

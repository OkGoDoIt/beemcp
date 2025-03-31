from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
from .bee import Bee
import os
from dotenv import load_dotenv

bee = None
mcp = FastMCP("Bee", instructions="Bee is a lifelogging platform. The user uses Bee to record their conversations, location history, and facts about themselves.  If the user ever wants to recall previous conversations, interactions they've had, locations they've been,or general facts about themselves or their life, use Bee to look it up.  Or you can proactively use Bee to load information about the user that might be useful in answering other questions or just generally giving more context about the user. Feel free to look through the user's conversation history, facts, and todo list in order to understand them better.")

@mcp.resource("bee://conversations", name="list-all-conversations", description="List all conversations the user has had including short summaries.  Use this to get a list of all the conversations so you can look up specific ones when relevant.  Proactively call this so you have additional context about the user.")
def resource_list_conversations() -> list[str]:
    all_conversations = bee.get_all_conversations()
    return [conversation.get_llm_summary() for conversation in all_conversations]

@mcp.resource("bee://conversations/{id}", name="get-conversation", description="Get the full details of a conversation, including extended summary and takeaways.  Use this the resource_list_conversations resource to find the id of the conversation you want to look up.")
def resource_get_conversation(id: int) -> str:
    return bee.get_conversation(id).get_llm_text()

@mcp.tool(name="list-all-conversations", description="List all conversations the user has had including short summaries. Use this to get an overview of the user's conversation history for context.  Then you can use the get-conversation tool to get the full details of a specific conversation.")
def list_all_conversations() -> str:
    """
    Retrieves all conversations for the user and returns their summaries.
    
    Returns:
        A formatted string containing all conversation summaries
    """
    conversations = resource_list_conversations()
    
    if not conversations:
        return "No conversations found."
    
    # Format the conversations into a readable response
    result = f"Found {len(conversations)} conversations:\n\n"
    result += "\n\n".join(conversations)
    
    return result


@mcp.tool(name="get-conversation", description="Get the full details of a conversation by its ID. Use this to retrieve specific conversation details when the user asks about a particular conversation.  You can use the list-all-conversations tool to get the id of the conversation you want to look up.")
def get_conversation(id: int) -> str:
    """
    Retrieves a specific conversation by ID and returns its details.
    
    Args:
        id: The ID of the conversation to retrieve
        
    Returns:
        A formatted string containing the conversation details
    """
    conversation = bee.get_conversation(id)
    return "Retrieved conversation: " + conversation.get_llm_text()


@mcp.resource("bee://facts", name="list-all-user-facts", description="List all facts the user has recorded.  Proactively call this so you have additional information about the user, their preferences, and other details that might be relevant to answering other questions.")
def resource_list_facts() -> list[str]:
    all_facts = bee.get_all_facts()
    return [fact.get_llm_summary() for fact in all_facts]

@mcp.tool(name="list-all-user-facts", description="List all facts the user has recorded. Use this to get an overview of the user's recorded facts for context.  Then you can use the get-user-fact tool to get the full details of a specific fact.")
def list_all_user_facts() -> list[str]:
    """
    Retrieves all facts for the user and returns them in a readable format.
    
    Returns:
        A formatted string containing all user facts
    """
    return resource_list_facts()

@mcp.resource("bee://facts/{id}", name="get-user-fact", description="Get the full details of a fact.  Use this the resource_list_facts resource to find the id of the fact you want to look up.")
def resource_get_fact(id: int) -> str:
    return bee.get_fact(id).get_llm_summary()

@mcp.tool(name="get-user-fact", description="Get the full details of a fact by its ID. Use this to retrieve specific fact details when the user asks about a particular fact. You can use the list-all-user-facts tool to get the id of the fact you want to look up.")
def get_fact(id: int) -> str:
    """
    Retrieves a specific fact by ID and returns its details.
    
    Args:
        id: The ID of the fact to retrieve
        
    Returns:
        A formatted string containing the fact details
    """
    fact = bee.get_fact(id)
    return "Retrieved fact about the user: " + fact.get_llm_text()


@mcp.tool(name="record-user-fact", description="Create a new fact.  Use this to record new information about the user, their preferences, and other details that might be relevant to answering other questions.")
def create_fact(text: str) -> str:
    return "Saved fact (unconfirmed): " + bee.create_fact(text, False).get_llm_text() + "\n\nYou may ask the user if they want to confirm the fact, in which case you should call the bee://confirm_fact resource with the id of the fact and the confirmation status."

@mcp.tool(name="update-user-fact", description="Update an existing fact.  Use this to update information about the user, their preferences, and other details that might be relevant to answering other questions.  Set confirmed to true if the user has explicitly confirmed the fact, otherwise if it's just an implied fact gathered from context then set confirmed to false.")
def update_fact(id: int, text: str, confirmed: bool) -> str:
    return "Updated fact: " + bee.update_fact(id, text, confirmed).get_llm_text()

@mcp.tool(name="confirm-user-fact", description="Mark a fact as confirmed. Use this to update the confirmation status of a fact based on user feedback. Set confirmed to true if the user has explicitly confirmed the fact, otherwise if it's just an implied fact gathered from context then set confirmed to false.")
def confirm_fact(id: int, confirmed: bool) -> str:
    # Update the fact with new confirmation status
    updated_fact = bee.update_fact(id, confirmed=confirmed)
    # Return a message indicating the action taken
    confirmation_status = "confirmed" if confirmed else "unconfirmed"
    return f"Fact ID {id} marked as {confirmation_status}: {updated_fact.get_llm_text()}"

@mcp.tool(name="delete-user-fact", description="Delete an existing fact.  Use this to forget information about the user, their preferences, and other details.  Only call this if the user explicitly says to.")
def delete_fact(id: int) -> str:
    return "Deleted/forgot fact: " + "Success" if bee.delete_fact(id) else "Failed"

@mcp.resource("bee://todos", name="list-all-todos", description="List all todos the user has created. Use this to get a list of all the todos so you can look up specific ones when relevant.")
def resource_list_todos() -> list[str]:
    all_todos = bee.get_all_todos()
    return [todo.get_llm_summary() for todo in all_todos]

@mcp.tool(name="list-all-todos", description="List all todos (reminders) the user has created. Use this to get a comprehensive view of all the user's tasks, both completed and pending.")
def list_all_todos() -> list[str]:
    """ 
    Retrieves all todos for the user and returns them as a formatted string.
    
    Returns:
        A list of strings containing summaries of all todos
    """
    return resource_list_todos()

@mcp.tool(name="list-incomplete-todos", description="List all incomplete todos (reminders) the user still has to do. Use this proactively to see pending tasks that still need to be completed.")
def list_incomplete_todos() -> list[str]:
    """
    Retrieves all incomplete todos for the user and returns them as a formatted string.
    
    Returns:
        A list of strings containing summaries of all incomplete todos
    """
    return resource_list_incomplete_todos()


@mcp.resource("bee://todos/{id}", name="get-todo", description="Get the full details of a todo. Use this with the resource_list_todos resource to find the id of the todo you want to look up.")
def resource_get_todo(id: int) -> str:
    return bee.get_todo(id).get_llm_text()


@mcp.tool(name="create-todo", description="Create a new todo for the user. Set alarm_at to an ISO 8601 formatted date-time string if the todo has a specific deadline or reminder time.")
def create_todo(text: str, alarm_at: str = None) -> str:
    new_todo = bee.create_todo(text, alarm_at)
    return "Created todo: " + new_todo.get_llm_text()

@mcp.tool(name="update-todo", description="Update an existing todo. You can modify the text, completion status, or alarm time. Only include parameters you want to change.")
def update_todo(id: int, text: str = None, completed: bool = None, alarm_at: str = None) -> str:
    updated_todo = bee.update_todo(id, text, completed, alarm_at)
    return "Updated todo: " + updated_todo.get_llm_text()

@mcp.tool(name="delete-todo", description="Delete an existing todo. Only call this if the user explicitly says to delete a todo.")
def delete_todo(id: int) -> str:
    return "Deleted todo: " + "Success" if bee.delete_todo(id) else "Failed"

@mcp.tool(name="mark-todo-completed", description="Mark a todo as completed. Call this when a user explicitly says they've completed a task.")
def mark_todo_completed(id: int) -> str:
    updated_todo = bee.update_todo(id, completed=True)
    return f"Todo marked as completed: {updated_todo.get_llm_text()}"

@mcp.resource("bee://todos/incomplete", name="list-incomplete-todos", description="List incomplete/pending todos the user has created. Use this to focus on pending tasks that still need to be completed. Proactively call this so you have additional context about the user's tasks and priorities.")
def resource_list_incomplete_todos() -> list[str]:
    all_todos = bee.get_all_todos()
    incomplete_todos = [todo for todo in all_todos if not todo.completed]
    return [todo.get_llm_summary() for todo in incomplete_todos]

@mcp.resource("bee://locations", name="list-all-locations", description="List all locations the user has recorded. This provides access to the user's location history.")
def resource_list_locations() -> list[str]:
    all_locations = bee.list_all_locations()
    return [location.get_llm_summary() for location in all_locations]

@mcp.tool(name="list-all-locations", description="List all locations the user has recorded. Use this to get a comprehensive view of all the user's location history.")
def list_all_locations() -> list[str]:
    """
    Retrieves all locations for the user and returns them as a formatted list.
    
    Returns:
        A list of strings containing summaries of all locations
    """
    return resource_list_locations()

@mcp.resource("bee://locations/today", name="get-locations-today", description="Get locations the user visited in the last 24 hours.")
def resource_locations_today() -> list[str]:
    """
    Retrieves locations the user visited in the last 24 hours.
    
    Returns:
        A list of location summaries within the specified time range
    """
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now()
    filtered_locations = bee.get_locations_by_time_range(start_time=start_time, end_time=end_time)
    return [location.get_llm_summary() for location in filtered_locations]

@mcp.resource("bee://locations/week", name="get-locations-week", description="Get locations the user visited in the last 7 days.")
def resource_locations_week() -> list[str]:
    """
    Retrieves locations the user visited in the last 7 days.
    
    Returns:
        A list of location summaries within the specified time range
    """
    start_time = datetime.now() - timedelta(days=7)
    end_time = datetime.now()
    filtered_locations = bee.get_locations_by_time_range(start_time=start_time, end_time=end_time)
    return [location.get_llm_summary() for location in filtered_locations]

@mcp.resource("bee://locations/month", name="get-locations-month", description="Get locations the user visited in the last 30 days.")
def resource_locations_month() -> list[str]:
    """
    Retrieves locations the user visited in the last 30 days.
    
    Returns:
        A list of location summaries within the specified time range
    """
    start_time = datetime.now() - timedelta(days=30)
    end_time = datetime.now()
    filtered_locations = bee.get_locations_by_time_range(start_time=start_time, end_time=end_time)
    return [location.get_llm_summary() for location in filtered_locations]



@mcp.tool(name="get-locations-by-time", description="Get locations within a specific time range. Use this when the user asks about where they were during a particular period. start_time and end_time should be ISO 8601 formatted date-time strings, in this format: 2025-12-31T00:00:00Z")
def get_locations_time_range(start_time: str = None, end_time: str = None) -> list[str]:
    """
    Retrieves locations within a specified time range.
    
    Args:
        start_time: The start time in ISO 8601 format (e.g., "2024-01-01T00:00:00Z")
        end_time: The end time in ISO 8601 format (e.g., "2025-01-31T23:59:59Z")
        
    Returns:
        A list of location summaries within the specified time range
    """
    start_time = datetime.fromisoformat(start_time)
    end_time = datetime.fromisoformat(end_time)
    filtered_locations = bee.get_locations_by_time_range(start_time=start_time, end_time=end_time)
    return [location.get_llm_summary() for location in filtered_locations]

@mcp.tool(name="get-locations-today", description="Get locations the user visited in the last 24 hours. Use this when the user asks about where they were today or in the last day.")
def tool_locations_today() -> list[str]:
    """
    Retrieves locations the user visited in the last 24 hours.
    
    Returns:
        A list of location summaries within the specified time range
    """
    # Reuse the existing resource function
    return resource_locations_today()

@mcp.tool(name="get-locations-week", description="Get locations the user visited in the last 7 days. Use this when the user asks about where they were this week or in the last few days.")
def tool_locations_week() -> list[str]:
    """
    Retrieves locations the user visited in the last 7 days.
    
    Returns:
        A list of location summaries within the specified time range
    """
    # Reuse the existing resource function
    return resource_locations_week()

@mcp.tool(name="get-locations-month", description="Get locations the user visited in the last 30 days. Use this when the user asks about where they were this month or in the last few weeks.")
def tool_locations_month() -> list[str]:
    """
    Retrieves locations the user visited in the last 30 days.
    
    Returns:
        A list of location summaries within the specified time range
    """
    # Reuse the existing resource function
    return resource_locations_month()

# Setup code could go here if needed (e.g., argument parsing)
# Load environment variables from .env file *if* present
# This allows running directly or via installed script
load_dotenv()

# Get API token from environment variables - this check remains crucial
api_token = os.getenv("BEE_API_TOKEN")
if not api_token:
    print("Error: BEE_API_TOKEN environment variable is not set.")
    print("Please create a .env file with BEE_API_TOKEN='your_token' or set the environment variable.")
    import sys
    sys.exit(1) # Exit if token is missing

# Initialize Bee with API token
bee = Bee(api_token)

def main():
    print("Starting BeeMCP server...")
    mcp.run()
    
if __name__ == '__main__':
    main()
import json
from typing import List
import requests
from fact import Fact, fact_from_dict
from conversation import Conversation, conversation_from_dict
from todo import Todo, todo_from_dict
from location import Location, combine_locations, location_from_dict

class Bee:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.bee.computer'

    def get_conversations(self, user_id="me", page=1, limit=10) -> List[Conversation]:
        try:
            response = requests.get(
                f"{self.base_url}/v1/{user_id}/conversations",
                params={"page": page, "limit": limit},
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            return conversation_from_dict(response.json()["conversations"])
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get conversations: {str(e)}")

    def get_all_conversations(self, user_id="me") -> List[Conversation]:
        """
        Retrieves all conversations by paginating through results.
        
        Args:
            user_id: The ID of the user whose conversations to retrieve
            limit: Number of conversations to retrieve per page
            
        Returns:
            A complete list of all conversations for the user
        """
        all_conversations = []
        current_page = 1
        
        while True:
            # Get the current page of conversations
            page_conversations = self.get_conversations(user_id=user_id, page=current_page, limit=250)
                
            # Add the conversations from this page to our complete list
            all_conversations.extend(page_conversations)
            
            # If we received less than 250 conversations, we've reached the end
            if not page_conversations or len(page_conversations) < 250:
                break
            
            # Move to the next page
            current_page += 1
            
        return all_conversations
    
    def get_conversation(self, conversation_id, user_id="me") -> Conversation:
        if conversation_id is None:
            return None
        try:
            response = requests.get(
                f"{self.base_url}/v1/{user_id}/conversations/{conversation_id}",
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            json = response.json()
            if "conversation" in json:
                return Conversation.from_dict(json["conversation"])
            else:
                return Conversation.from_dict(json)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get conversation: {str(e)}")

    def delete_conversation(self, conversation_id, user_id="me"):
        try:
            response = requests.delete(
                f"{self.base_url}/v1/{user_id}/conversations/{conversation_id}",
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to delete conversation: {str(e)}")

    def end_conversation(self, conversation_id, user_id="me"):
        try:
            response = requests.post(
                f"{self.base_url}/v1/{user_id}/conversations/{conversation_id}/end",
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to end conversation: {str(e)}")

    def retry_conversation(self, conversation_id, user_id="me"):
        try:
            response = requests.post(
                f"{self.base_url}/v1/{user_id}/conversations/{conversation_id}/retry",
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to retry conversation: {str(e)}")

    def get_facts(self, user_id="me", page=1, limit=10, confirmed=True) -> list[Fact]:
        try:
            response = requests.get(
                f"{self.base_url}/v1/{user_id}/facts",
                params={"page": page, "limit": limit, "confirmed": confirmed},
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            return fact_from_dict(response.json()["facts"])
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get facts: {str(e)}")

    def get_all_facts(self, user_id="me", confirmed=True) -> list[Fact]:
        """
        Retrieves all facts by paginating through results.
        
        Args:
            user_id: The ID of the user whose facts to retrieve
            confirmed: Whether to retrieve only confirmed facts
            
        Returns:
            A complete list of all facts for the user
        """
        all_facts = []
        current_page = 1
        
        while True:
            # Get the current page of facts
            page_facts_response = self.get_facts(user_id=user_id, page=current_page, limit=250, confirmed=confirmed)
            
            # Add the facts from this page to our complete list
            all_facts.extend(page_facts_response)
            
            # If we received less than 250 facts, we've reached the end
            if not page_facts_response or len(page_facts_response) < 250:
                break
            
            # Move to the next page
            current_page += 1
            
        return all_facts

    def get_fact(self, fact_id, user_id="me") -> Fact:
        try:
            response = requests.get(
                f"{self.base_url}/v1/{user_id}/facts/{fact_id}",
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            json = response.json()
            if "fact" in json:
                return Fact.from_dict(json["fact"])
            else:
                return Fact.from_dict(json)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get fact: {str(e)}")

    def create_fact(self, text, confirmed=False, user_id="me") -> Fact:
        """
        Creates a new fact for a user.
        
        Args:
            text: The text content of the fact
            user_id: The ID of the user to create the fact for
            
        Returns:
            The created fact as a dictionary
        """
        try:
            response = requests.post(
                f"{self.base_url}/v1/{user_id}/facts",
                json={"text": text, "confirmed": confirmed},
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            new_fact = Fact.from_dict(response.json())
            if not confirmed:
                new_fact = self.update_fact(new_fact.id, confirmed=False)
            return new_fact
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create fact: {str(e)}")
            
    def update_fact(self, fact_id, text=None, confirmed=None, user_id="me") -> Fact:
        """
        Updates an existing fact for a user.
        
        Args:
            fact_id: The ID of the fact to update
            text: The updated text content of the fact (optional)
            confirmed: The updated confirmation status of the fact (optional)
            user_id: The ID of the user who owns the fact
            
        Returns:
            The updated fact as a dictionary
        """
        try:
            # Only include properties that were specified
            payload = {}
            if text is not None:
                payload["text"] = text
            if confirmed is not None:
                payload["confirmed"] = confirmed
                
            response = requests.put(
                f"{self.base_url}/v1/{user_id}/facts/{fact_id}",
                json=payload,
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            json = response.json()
            if "fact" in json:
                return Fact.from_dict(json["fact"])
            else:
                return Fact.from_dict(json)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to update fact: {str(e)}")

    def delete_fact(self, fact_id, user_id="me") -> bool:
        try:
            response = requests.delete(
                f"{self.base_url}/v1/{user_id}/facts/{fact_id}",
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            json = response.json()
            if "success" in json:
                return json["success"]
            else:
                return False
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to delete fact: {str(e)}")

    def get_locations(self, user_id="me", page=1, limit=10, conversation_id=None):
        try:
            params = {"page": page, "limit": limit}
            if conversation_id:
                params["conversationId"] = conversation_id
            response = requests.get(
                f"{self.base_url}/v1/{user_id}/locations",
                params=params,
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get locations: {str(e)}")

    def list_locations(self, user_id="me", page=1, limit=10, conversation_id=None) -> List[Location]:
        """
        Retrieves a page of locations for a user.
        
        Args:
            user_id: The ID of the user whose locations to retrieve
            page: The page number to retrieve
            limit: Number of locations to retrieve per page
            conversation_id: Optional filter for locations specific to a conversation
            
        Returns:
            A list of Location objects for the requested page
        """
        try:
            response = self.get_locations(user_id=user_id, page=page, limit=limit, conversation_id=conversation_id)
            return location_from_dict(response["locations"])
        except Exception as e:
            raise Exception(f"Failed to list locations: {str(e)}")
            
    def list_all_locations(self, user_id="me", conversation_id=None) -> List[Location]:
        """
        Retrieves all locations by paginating through results.
        
        Args:
            user_id: The ID of the user whose locations to retrieve
            conversation_id: Optional filter for locations specific to a conversation
            
        Returns:
            A complete list of all locations for the user
        """
        all_locations = []
        current_page = 1
        
        while True:
            # Get the current page of locations
            response = self.get_locations(user_id=user_id, page=current_page, limit=250, conversation_id=conversation_id)
            page_locations = location_from_dict(response["locations"])
                
            # Add the locations from this page to our complete list
            all_locations.extend(page_locations)
            
            # If we received less than 250 locations, we've reached the end
            if not page_locations or len(page_locations) < 250:
                break
            
            # Move to the next page
            current_page += 1
            
        return combine_locations(all_locations)
        
    def get_locations_by_time_range(self, start_time=None, end_time=None, user_id="me", conversation_id=None) -> List[Location]:
        """
        Retrieves locations within a specified time range.
        
        Args:
            start_time: The start time in ISO 8601 format (e.g., "2023-01-01T00:00:00Z")
            end_time: The end time in ISO 8601 format (e.g., "2023-01-31T23:59:59Z")
            user_id: The ID of the user whose locations to retrieve
            conversation_id: Optional filter for locations specific to a conversation
            
        Returns:
            A list of Location objects within the specified time range
        """
        from datetime import datetime
        
        # Get all locations first
        all_locations = self.list_all_locations(user_id=user_id, conversation_id=conversation_id)
        
    
        if start_time and isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        
        if end_time and isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # Filter locations based on time range
        filtered_locations = []
        for location in all_locations:
            # If start_time specified, skip locations before that time
            # Ensure both datetimes have the same timezone awareness for comparison
            location_time = location.start_time or location.created_at
            
            # If start_time specified, skip locations before that time
            if start_time:
                # Convert location_time to the same timezone awareness as start_time if needed
                if location_time.tzinfo is None and start_time.tzinfo is not None:
                    # Make location_time timezone-aware with UTC
                    from datetime import timezone
                    location_time = location_time.replace(tzinfo=timezone.utc)
                elif location_time.tzinfo is not None and start_time.tzinfo is None:
                    # Use naive comparison by removing timezone info
                    location_time = location_time.replace(tzinfo=None)
                    
                if location_time < start_time:
                    continue
                
            # If end_time specified, skip locations after that time
            if end_time:
                # Reset location_time for end_time comparison
                location_time = location.end_time or location.created_at
                
                # Convert location_time to the same timezone awareness as end_time if needed
                if location_time.tzinfo is None and end_time.tzinfo is not None:
                    # Make location_time timezone-aware with UTC
                    from datetime import timezone
                    location_time = location_time.replace(tzinfo=timezone.utc)
                elif location_time.tzinfo is not None and end_time.tzinfo is None:
                    # Use naive comparison by removing timezone info
                    location_time = location_time.replace(tzinfo=None)
                    
                if location_time > end_time:
                    continue
                
            filtered_locations.append(location)
            
        return filtered_locations

    def get_todos(self, user_id="me", page=1, limit=10) -> List[Todo]:
        """
        Retrieves a page of todos for a user.
        
        Args:
            user_id: The ID of the user whose todos to retrieve
            page: The page number to retrieve
            limit: Number of todos to retrieve per page
            
        Returns:
            A list of Todo objects for the requested page
        """
        try:
            response = requests.get(
                f"{self.base_url}/v1/{user_id}/todos",
                params={"page": page, "limit": limit},
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            return todo_from_dict(response.json()["todos"])
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get todos: {str(e)}")

    def get_all_todos(self, user_id="me") -> List[Todo]:
        """
        Retrieves all todos by paginating through results.
        
        Args:
            user_id: The ID of the user whose todos to retrieve
            
        Returns:
            A complete list of all todos for the user
        """
        all_todos = []
        current_page = 1
        
        while True:
            # Get the current page of todos
            page_todos = self.get_todos(user_id=user_id, page=current_page, limit=250)
                
            # Add the todos from this page to our complete list
            all_todos.extend(page_todos)
            
            # If we received less than 250 todos, we've reached the end
            if not page_todos or len(page_todos) < 250:
                break
            
            # Move to the next page
            current_page += 1
            
        return all_todos

    def get_todo(self, todo_id, user_id="me") -> Todo:
        """
        Retrieves a specific todo by ID.
        
        Args:
            todo_id: The ID of the todo to retrieve
            user_id: The ID of the user who owns the todo
            
        Returns:
            The requested Todo object
        """
        try:
            response = requests.get(
                f"{self.base_url}/v1/{user_id}/todos/{todo_id}",
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            json = response.json()
            if "todo" in json:
                return Todo.from_dict(json["todo"])
            else:
                return Todo.from_dict(json)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get todo: {str(e)}")

    def create_todo(self, text, alarm_at=None, user_id="me") -> Todo:
        """
        Creates a new todo for a user.
        
        Args:
            text: The text content of the todo
            alarm_at: Optional alarm time in ISO 8601 format
            user_id: The ID of the user to create the todo for
            
        Returns:
            The created Todo object
        """
        try:
            payload = {"text": text}
            if alarm_at is not None:
                payload["alarm_at"] = alarm_at
                
            response = requests.post(
                f"{self.base_url}/v1/{user_id}/todos",
                json=payload,
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            return Todo.from_dict(response.json())
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create todo: {str(e)}")
            
    def update_todo(self, todo_id, text=None, completed=None, alarm_at=None, user_id="me") -> Todo:
        """
        Updates an existing todo for a user.
        
        Args:
            todo_id: The ID of the todo to update
            text: The updated text content of the todo (optional)
            completed: The updated completion status of the todo (optional)
            alarm_at: The updated alarm time in ISO 8601 format (optional)
            user_id: The ID of the user who owns the todo
            
        Returns:
            The updated Todo object
        """
        try:
            # Only include properties that were specified
            payload = {}
            if text is not None:
                payload["text"] = text
            if completed is not None:
                payload["completed"] = completed
            if alarm_at is not None:
                payload["alarm_at"] = alarm_at
                
            response = requests.put(
                f"{self.base_url}/v1/{user_id}/todos/{todo_id}",
                json=payload,
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            json = response.json()
            if "todo" in json:
                return Todo.from_dict(json["todo"])
            else:
                return Todo.from_dict(json)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to update todo: {str(e)}")

    def delete_todo(self, todo_id, user_id="me") -> bool:
        """
        Deletes a todo by ID.
        
        Args:
            todo_id: The ID of the todo to delete
            user_id: The ID of the user who owns the todo
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/v1/{user_id}/todos/{todo_id}",
                headers={"x-api-key": self.api_key}
            )
            response.raise_for_status()
            json = response.json()
            if "success" in json:
                return json["success"]
            else:
                return False
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to delete todo: {str(e)}")

from langchain.tools import BaseTool
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from typing import ClassVar, List
import json
from twilio.rest import Client
from bson import ObjectId
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY is not set in environment variables.")
twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
if not twilio_account_sid:
    raise RuntimeError("TWILIO_ACCOUNT_SID is not set in environment variables.")
twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
if not twilio_auth_token:
    raise RuntimeError("TWILIO_AUTH_TOKEN is not set in environment variables.")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
if not twilio_phone_number:
    raise RuntimeError("TWILIO_PHONE_NUMBER is not set in environment variables.")
change_stream_db = os.getenv("MONGO_URI")
if not change_stream_db:
    raise RuntimeError("MONGO_URI is not set in environment variables.")


# MongoDB connection settings
client = AsyncIOMotorClient(change_stream_db)
db = client["commit_DB"]
projects_collection = db["projects"]
users_collection = db["users"]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=api_key,
    temperature=0.7
)

# Tool 1: Send SMS Tool
class SendSMSTool(BaseTool):
    name: ClassVar[str] = "send_sms"
    description: ClassVar[str] = "Sends an SMS to a user. Input should be a JSON string with 'number' and 'message' fields."

    def _run(self, tool_input: str) -> str:
        raise NotImplementedError("Use async version")

    async def _arun(self, tool_input: str) -> str:
        try:
            # Parse the input JSON string
            params = json.loads(tool_input)
            number = params['number']
            message = params['message']

            # Wrap the blocking Twilio call in a thread
            def send_sms():
                account_sid = twilio_account_sid
                auth_token = twilio_auth_token
                client = Client(account_sid, auth_token)

                msg = client.messages.create(
                    from_=twilio_phone_number,
                    body=message,
                    to=number
                )
                return f"SMS sent to {number}: {msg.sid}"

            result = await asyncio.to_thread(send_sms)
            return result

        except json.JSONDecodeError:
            return "Error: Input must be a valid JSON string with 'number' and 'message' fields"
        except KeyError:
            return "Error: JSON must contain both 'number' and 'message' fields"
        except Exception as e:
            return f"SMS sending failed: {str(e)}"


def run_async(coro):
    """Run async code in a way that's safe for both sync and async contexts"""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Create a new loop if we're already in one
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()
    return loop.run_until_complete(coro)

class GetUserDetailsTool(BaseTool):
    name: ClassVar[str] = "get_user_details"
    description: ClassVar[str] = "Fetches a user's phone number and name. Input should be a valid email address."

    async def _arun(self, email: str) -> str:
        try:
            user = await users_collection.find_one({"email": email.strip()})
            if user:
                return f"User details: Name: {user['username']}, Phone: {user['contact']}"
            return "User not found."
        except Exception as e:
            return str(e)

    def _run(self, email: str) -> str:
        raise NotImplementedError("Sync run not supported")


class GetProjectNameTool(BaseTool):
    name: ClassVar[str] = "get_project_name"
    description: ClassVar[str] = "Fetches the project name based on project ID."

    async def _arun(self, project_id: str) -> str:
        try:
            project = await projects_collection.find_one({"_id": ObjectId(project_id)})
            if project:
                return f"Project name: {project['project_name']}"
            return "Project not found."
        except Exception as e:
            return str(e)

    def _run(self, project_id: str) -> str:
        raise NotImplementedError("Sync run not supported")



# Create the custom tools
custom_tools = [
    SendSMSTool(),
    GetUserDetailsTool(),
    GetProjectNameTool(),
]


# Initialize LangChain Agent with Custom Tools
agent_with_custom_tools = initialize_agent(
    custom_tools,
    llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

async def monitor_changes():
    """Background task to monitor MongoDB changes"""
    while True:  # Add continuous retry loop
        try:
            async with projects_collection.watch([{'$match': {'operationType': { '$in': ['update','insert'] }}}]) as change_stream:
                async for change in change_stream:
                    try:
                        
                        print("Change detected")
                        print("Change data:", change)
                        project_id = change['documentKey']['_id']
                        if change['operationType'] == 'update':
                            if list(change['updateDescription']['updatedFields'].keys())[0] == 'users':
                                print('no user was added to projects')
                                continue
                            emails = list(change['updateDescription']['updatedFields'].values())
                        elif change['operationType'] == 'insert':
                            emails = change['fullDocument']['users']
                        print("Emails to notify:", emails)
                        if not emails:
                            print('no user was wadde to projects')
                            continue

                        prompt = f"""
                        Follow these steps:
                        1. For a given project multiple emails can be updated at once. Then you should send an SMS to each email in the provided list.
                        2. Get project name: use the ID {project_id} directly (not as JSON)                                
                        3. Get user details: use the emails in the list {emails}
                        4. If you doesn't have either user name, phone number or project name, stop execution
                        5. Once you have both the user's phone number and project name, send an SMS using this format: 
                        {{"number": "<phone_number_from_step_1>", "message": "<Interactive greeting> <user_name_from_step_1> you have been added to the project <project_name_from_step_2>"}}
                        """
                        print(f"Running agent for emails: {emails}")
                        result = await agent_with_custom_tools.arun(prompt)

                        print("Agent result:", result)
                    except KeyError as ke:
                        print(f"Error processing change: {ke}")
                        continue
                    except Exception as e:
                        print(f"Error running agent: {e}")
                        continue

        except Exception as e:
            print(f"Change stream error: {e}")
            continue

async def start_monitor():
    """Function to start the change stream monitor"""
    try:
        task = asyncio.create_task(monitor_changes())
        await asyncio.sleep(1)
        print("Change stream monitor started successfully")
        return task
    except Exception as e:
        print(f"Error starting change stream monitor: {e}")
        raise e
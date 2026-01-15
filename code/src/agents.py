"""Multi-agent orchestration for the AI Assistant."""

from zoneinfo import ZoneInfo
from tzlocal import get_localzone
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

from .config import config
from .logger import logger
from .tools import WeatherTools, SearchTools


class MultiAgentAssistant:
    """Multi-agent AI assistant orchestrator."""

    def __init__(self):
        """Initialize the multi-agent assistant."""
        self.model_client = self._create_model_client()
        self.agents = []
        self.team = None

    def _create_model_client(self) -> OpenAIChatCompletionClient:
        """Create OpenAI model client."""
        return OpenAIChatCompletionClient(
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=config.OPENAI_TEMPERATURE,
        )

    def _get_timezone(self) -> str:
        """Get current timezone."""
        try:
            return str(ZoneInfo(str(get_localzone())))
        except Exception:
            return config.DEFAULT_TIMEZONE

    async def _create_weather_agent(self) -> AssistantAgent:
        """Create weather assistant agent."""
        try:
            weather_tools = WeatherTools()
            tools = await weather_tools.as_function_tools()
            logger.info(f"Created weather agent with {len(tools)} tools")

            return AssistantAgent(
                name="WeatherAssistant",
                description=(
                    "An AI assistant that provides weather information. "
                    "Answers questions about current weather, forecasts, and precipitation. "
                    "Use me for queries like 'weather in Mumbai' or 'will it rain tomorrow?'"
                ),
                model_client=self.model_client,
                tools=tools,
                system_message=f"""You are a weather information assistant.
Use the available tools to provide accurate weather data and forecasts.
Always include temperature, conditions, and relevant precipitation info.
Current timezone: {self._get_timezone()}
Be concise and user-friendly in your responses.""",
                reflect_on_tool_use=True,
            )

        except Exception as e:
            logger.warning(f"Weather agent creation failed: {e}")
            return None

    async def _create_search_agent(self) -> AssistantAgent:
        """Create search assistant agent."""
        try:
            search_tools = SearchTools()
            tools = await search_tools.as_function_tools()
            logger.info(f"Created search agent with {len(tools)} tools")

            return AssistantAgent(
                name="SearchAssistant",
                description=(
                    "An AI assistant that performs web searches and research. "
                    "Use me for finding current information, news, facts, or detailed research. "
                    "I can do quick searches or comprehensive deep dives."
                ),
                model_client=self.model_client,
                tools=tools,
                system_message=f"""You are a web search and research assistant.
Use web_search for quick queries and research for in-depth information.
Always cite sources and provide comprehensive, accurate information.
Current timezone: {self._get_timezone()}
Be thorough but concise in your responses.""",
                reflect_on_tool_use=True,
            )

        except Exception as e:
            logger.warning(f"Search agent creation failed: {e}")
            return None

    async def initialize(self):
        """Initialize all agents and create the team."""
        try:
            logger.info("Initializing multi-agent assistant...")

            # Create specialized agents
            weather_agent = await self._create_weather_agent()
            search_agent = await self._create_search_agent()

            # Collect successfully created agents
            self.agents = [agent for agent in [weather_agent, search_agent] if agent]

            if not self.agents:
                raise RuntimeError("No agents were successfully created")

            logger.info(f"Created {len(self.agents)} agents")

            # Create the orchestrator team
            termination_condition = TextMentionTermination("TERMINATE")

            self.team = MagenticOneGroupChat(
                self.agents,
                model_client=self.model_client,
                termination_condition=termination_condition,
                max_turns=15,
            )

            logger.info("Multi-agent assistant initialized successfully")

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    async def process_message(self, message: str) -> str:
        """
        Process a user message through the multi-agent system.

        Args:
            message: User's message/query

        Returns:
            Assistant's response
        """
        try:
            if not self.team:
                raise RuntimeError("Assistant not initialized. Call initialize() first.")

            logger.info(f"Processing message: {message[:50]}...")

            # Run the team chat
            result = await self.team.run(task=message)

            # Extract the response
            if hasattr(result, "messages") and result.messages:
                # Get the last message from the conversation
                last_message = result.messages[-1]
                if hasattr(last_message, "content"):
                    response = last_message.content
                else:
                    response = str(last_message)
            else:
                response = str(result)

            logger.info("Message processed successfully")
            return response

        except Exception as e:
            error_msg = f"Error processing message: {e}"
            logger.error(error_msg)
            return error_msg

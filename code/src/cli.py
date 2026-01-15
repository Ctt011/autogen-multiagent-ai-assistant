"""
Interactive CLI for the Multi-Agent AI Assistant.

This provides a user-friendly command-line interface for chatting with the assistant.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import uuid

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich import print as rprint

from .agents import MultiAgentAssistant
from .config import config
from .logger import logger
from .memory import ConversationMemory


class AssistantCLI:
    """Interactive command-line interface for the AI Assistant."""

    def __init__(self):
        """Initialize the CLI."""
        self.console = Console()
        self.assistant: Optional[MultiAgentAssistant] = None
        self.memory = ConversationMemory()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _print_welcome(self):
        """Print welcome message."""
        welcome_text = """
# Multi-Agent AI Assistant

Welcome! I'm your AI assistant powered by multiple specialized agents:

- **WeatherAssistant**: Get weather forecasts and current conditions
- **SearchAssistant**: Search the web and research topics

**Commands:**
- `/help` - Show this help message
- `/agents` - List available agents
- `/history` - View conversation history
- `/stats` - Show memory statistics
- `/clear` - Clear the screen
- `/quit` or `/exit` - Exit the assistant

**Tips:**
- Ask me about the weather: "What's the weather in Paris?"
- Search for information: "Latest news on AI developments"
- Get forecasts: "Will it rain tomorrow in Tokyo?"

---
        """
        self.console.print(Panel(Markdown(welcome_text), border_style="cyan"))

    def _print_help(self):
        """Print help message."""
        help_text = """
## Available Commands

- `/help` - Show this help message
- `/agents` - List available agents and their capabilities
- `/history` - View recent conversation history
- `/stats` - Show conversation memory statistics
- `/clear` - Clear the terminal screen
- `/quit`, `/exit` - Exit the assistant

## Example Queries

**Weather:**
- "What's the weather in London?"
- "Give me a 3-day forecast for Mumbai"
- "Current temperature in New York"

**Search:**
- "Latest developments in artificial intelligence"
- "Research quantum computing applications"
- "What's happening in tech news today?"
        """
        self.console.print(Panel(Markdown(help_text), border_style="green"))

    def _print_agents(self):
        """Print information about available agents."""
        if not self.assistant or not self.assistant.agents:
            self.console.print("[yellow]No agents available yet.[/yellow]")
            return

        agents_text = "## Available Agents\n\n"
        for agent in self.assistant.agents:
            agents_text += f"### {agent.name}\n"
            agents_text += f"{agent.description}\n\n"

        self.console.print(Panel(Markdown(agents_text), border_style="blue"))

    def _print_history(self):
        """Print recent conversation history."""
        messages = self.memory.get_session_history(self.session_id, limit=20)

        if not messages:
            self.console.print("[yellow]No conversation history yet.[/yellow]")
            return

        table = Table(title="Recent Conversation History", show_header=True, header_style="bold magenta")
        table.add_column("Time", style="dim", width=8)
        table.add_column("Role", width=10)
        table.add_column("Message", ratio=1)

        for msg in messages[-10:]:  # Show last 10
            timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")
            role = msg["role"].capitalize()
            content = msg["content"][:80] + "..." if len(msg["content"]) > 80 else msg["content"]

            if msg["agent_name"]:
                role = f"{role} ({msg['agent_name']})"

            table.add_row(timestamp, role, content)

        self.console.print(table)
        self.console.print(f"\n[dim]Total messages in this session: {len(messages)}[/dim]")

    def _print_stats(self):
        """Print conversation memory statistics."""
        stats = self.memory.get_statistics()

        stats_text = f"""## Conversation Memory Statistics

- **Total Messages**: {stats['total_messages']}
- **Total Sessions**: {stats['total_sessions']}
- **Oldest Message**: {stats['oldest_message_age_days']} days ago
- **Current Session**: {self.session_id}
        """

        self.console.print(Panel(Markdown(stats_text), border_style="magenta"))

    def _handle_command(self, user_input: str) -> bool:
        """
        Handle special commands.

        Args:
            user_input: User's input string

        Returns:
            True if should continue, False if should exit
        """
        command = user_input.lower().strip()

        if command in ["/quit", "/exit"]:
            self.console.print("\n[cyan]Goodbye![/cyan]\n")
            return False

        elif command == "/help":
            self._print_help()

        elif command == "/agents":
            self._print_agents()

        elif command == "/clear":
            self.console.clear()
            self._print_welcome()

        elif command == "/history":
            self._print_history()

        elif command == "/stats":
            self._print_stats()

        else:
            self.console.print(f"[yellow]Unknown command: {command}[/yellow]")
            self.console.print("[dim]Type /help for available commands.[/dim]")

        return True

    async def _initialize_assistant(self):
        """Initialize the multi-agent assistant."""
        try:
            with self.console.status("[bold cyan]Initializing assistant...", spinner="dots"):
                self.assistant = MultiAgentAssistant()
                await self.assistant.initialize()

            self.console.print("[green]✓ Assistant initialized successfully![/green]\n")

        except Exception as e:
            self.console.print(f"[red]✗ Initialization failed: {e}[/red]")
            logger.error(f"Assistant initialization failed: {e}")
            sys.exit(1)

    async def _process_query(self, query: str):
        """
        Process a user query.

        Args:
            query: User's query string
        """
        try:
            # Save user message to memory
            self.memory.save_message(
                session_id=self.session_id,
                role="user",
                content=query
            )

            with self.console.status("[bold cyan]Thinking...", spinner="dots"):
                response = await self.assistant.process_message(query)

            # Save assistant response to memory
            self.memory.save_message(
                session_id=self.session_id,
                role="assistant",
                content=response
            )

            # Display the response
            self.console.print()
            self.console.print(Panel(
                Markdown(response) if response else "[dim]No response[/dim]",
                title="Assistant",
                border_style="cyan",
            ))
            self.console.print()

        except Exception as e:
            self.console.print(f"\n[red]Error: {e}[/red]\n")
            logger.error(f"Query processing failed: {e}")

    async def run(self):
        """Run the interactive CLI."""
        try:
            # Clear screen and show welcome
            self.console.clear()
            self._print_welcome()

            # Validate configuration
            try:
                config.validate()
            except ValueError as e:
                self.console.print(f"[red]Configuration error: {e}[/red]")
                self.console.print("\n[yellow]Please set up your .env file with required API keys.[/yellow]")
                self.console.print("[dim]See .env.example for reference.[/dim]\n")
                return

            # Initialize assistant
            await self._initialize_assistant()

            # Main interaction loop
            while True:
                try:
                    # Get user input
                    user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()

                    if not user_input:
                        continue

                    # Handle commands
                    if user_input.startswith("/"):
                        should_continue = self._handle_command(user_input)
                        if not should_continue:
                            break
                        continue

                    # Process regular query
                    await self._process_query(user_input)

                except KeyboardInterrupt:
                    self.console.print("\n\n[cyan]Use /quit to exit[/cyan]")
                    continue

                except EOFError:
                    break

        except Exception as e:
            self.console.print(f"\n[red]Fatal error: {e}[/red]")
            logger.error(f"CLI fatal error: {e}")
            sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli = AssistantCLI()
    asyncio.run(cli.run())


if __name__ == "__main__":
    main()

"""Search tools for the Multi-Agent AI Assistant."""

import httpx
from typing import Dict, Any
from autogen_core.tools import FunctionTool

from ..config import config
from ..logger import logger


class SearchTools:
    """Web search tools using Tavily API."""

    def __init__(self):
        self.tavily_api_key = config.TAVILY_SEARCH_KEY
        self.tavily_url = "https://api.tavily.com/search"
        self.max_results = config.MAX_SEARCH_RESULTS

    async def _make_request(
        self,
        query: str,
        search_depth: str = "basic",
        max_results: int = None,
    ) -> Dict[str, Any]:
        """Make request to Tavily search API."""
        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "search_depth": search_depth,
            "include_answer": True,
            "max_results": max_results or self.max_results,
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self.tavily_url, json=payload)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Tavily search completed for: {query[:50]}...")
                return data

        except Exception as e:
            logger.error(f"Tavily API error for '{query}': {e}")
            raise

    def _format_results(self, data: Dict[str, Any], query: str) -> str:
        """Format search results into readable text."""
        try:
            results = []

            # Add AI-generated answer
            answer = data.get("answer", "")
            if answer:
                results.append(f"Answer: {answer}\n")

            # Add search results
            search_results = data.get("results", [])
            if search_results:
                results.append("Sources:")
                for i, result in enumerate(search_results, 1):
                    title = result.get("title", "No title")
                    url = result.get("url", "")
                    content = result.get("content", "")

                    # Truncate long content
                    if len(content) > 200:
                        content = content[:200] + "..."

                    results.append(f"\n{i}. {title}")
                    results.append(f"   {url}")
                    results.append(f"   {content}")

            if not results:
                return f"No results found for: {query}"

            return "\n".join(results)

        except Exception as e:
            logger.error(f"Error formatting results: {e}")
            return f"Error formatting results: {e}"

    async def web_search(self, query: str) -> str:
        """
        Perform a web search and return results.

        Args:
            query: Search query string

        Returns:
            Formatted search results with answer and sources
        """
        try:
            if not query or not query.strip():
                return "Error: Search query cannot be empty"

            logger.info(f"Web search: {query}")
            data = await self._make_request(query, search_depth="basic")
            result = self._format_results(data, query)
            return result

        except Exception as e:
            error_msg = f"Error performing search: {e}"
            logger.error(error_msg)
            return error_msg

    async def research(self, query: str) -> str:
        """
        Perform deep research on a topic.

        Args:
            query: Research query string

        Returns:
            Comprehensive research results with detailed information
        """
        try:
            if not query or not query.strip():
                return "Error: Research query cannot be empty"

            logger.info(f"Deep research: {query}")
            data = await self._make_request(query, search_depth="advanced", max_results=10)
            result = self._format_results(data, query)
            return result

        except Exception as e:
            error_msg = f"Error performing research: {e}"
            logger.error(error_msg)
            return error_msg

    async def as_function_tools(self):
        """Convert search methods to AutoGen function tools."""
        return [
            FunctionTool(self.web_search, description="Quick web search for general queries"),
            FunctionTool(self.research, description="Deep research for comprehensive information"),
        ]

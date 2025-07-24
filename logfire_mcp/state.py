from dataclasses import dataclass

from logfire.experimental.query_client import AsyncLogfireQueryClient


@dataclass
class MCPState:
    logfire_client: AsyncLogfireQueryClient

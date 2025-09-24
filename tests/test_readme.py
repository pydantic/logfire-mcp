from pathlib import Path
from typing import TypedDict

import pytest
from jinja2 import Environment, FileSystemLoader
from mcp.client.session import ClientSession

env = Environment(loader=FileSystemLoader(Path(__file__).parent))
template = env.get_template('README.md.jinja')


pytestmark = [pytest.mark.vcr, pytest.mark.anyio]


class Argument(TypedDict):
    name: str
    description: str
    type: str


class Tool(TypedDict):
    name: str
    description: str
    arguments: list[Argument]


async def test_generate_readme(session: ClientSession) -> None:
    tools: list[Tool] = []
    mcp_tools = await session.list_tools()

    for tool in mcp_tools.tools:
        assert tool.description
        description = tool.description.split('\n', 1)[0].strip()

        arguments: list[Argument] = []
        for argument_name, argument_schema in tool.inputSchema['properties'].items():
            arguments.append(
                {'name': argument_name, 'description': argument_schema['description'], 'type': argument_schema['type']}
            )
        tools.append({'name': tool.name, 'description': description, 'arguments': arguments})

    readme = template.render(tools=tools)
    with open('README.md', 'w') as f:
        f.write(readme)

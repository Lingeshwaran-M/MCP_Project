import sys
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
from db_tools import read_records, create_student, update_student, delete_student

server = Server("mcp-bot")


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="read_records",
            description="Read all students",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="create_student",
            description="Create a new student",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone_number": {"type": "string"}
                },
                "required": ["name", "email", "phone_number"]
            }
        ),
        Tool(
            name="update_student",
            description="Update a student's details",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "integer"},
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone_number": {"type": "string"}
                },
                "required": ["student_id"]
            }
        ),
        Tool(
            name="delete_student",
            description="Delete a student",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "integer"}
                },
                "required": ["student_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict | None):

    if name == "read_records":
        rows = read_records()

        if not rows:
            text = "No students found."
        else:
            lines = []
            for r in rows:
                lines.append(
                    f"{r['id']} | {r['name']} | {r['email']} | {r['phone_number']}"
                )
            text = "\n".join(lines)

        return [TextContent(type="text", text=text)]

    elif name == "create_student":
        student_id = create_student(
            arguments["name"],
            arguments["email"],
            arguments["phone_number"]
        )
        return [TextContent(type="text", text=f"Student created with ID: {student_id}")]

    elif name == "update_student":
        count = update_student(
            arguments["student_id"],
            arguments.get("name"),
            arguments.get("email"),
            arguments.get("phone_number")
        )
        return [TextContent(type="text", text=f"Updated {count} student(s).")]

    elif name == "delete_student":
        count = delete_student(arguments["student_id"])
        return [TextContent(type="text", text=f"Deleted {count} student(s).")]

    return [TextContent(type="text", text="Unknown tool")]


if __name__ == "__main__":

    from mcp.server.sse import SseServerTransport
    import uvicorn

    sse = SseServerTransport("/messages")

    async def app(scope, receive, send):
        if scope["type"] == "http":

            if scope["path"] == "/sse":
                async with sse.connect_sse(scope, receive, send) as streams:
                    await server.run(
                        streams[0],
                        streams[1],
                        server.create_initialization_options()
                    )

            elif scope["path"] == "/messages":
                await sse.handle_post_message(scope, receive, send)

    uvicorn.run(app, host="0.0.0.0", port=8000)
import streamlit as st
import requests
import json
import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession


MCP_SERVER_URL = "http://localhost:8000/sse"
OLLAMA_URL = "http://localhost:11434/api/chat"


st.set_page_config(page_title="MCP Bot")
st.title("🤖 MCP Bot")
st.caption("AI + MCP + MySQL")
st.divider()


async def call_mcp_tool(tool_name, arguments):
    async with sse_client(MCP_SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text

def run_tool(tool_name, arguments):
    return asyncio.run(call_mcp_tool(tool_name, arguments))


def clean_format(raw_text: str) -> str:

    if not raw_text:
        return "No records found."

    lines = raw_text.split("\n")

    table_lines = []
    headers = ["ID", "Name", "Email", "Phone"]
    

    table_lines.append("| " + " | ".join(headers) + " |")

    table_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    found_data = False
    for line in lines:
        if "|" in line and "ID" not in line and "---" not in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                # Format the data row
                row = f"| {parts[0]} | {parts[1]} | {parts[2]} | {parts[3]} |"
                table_lines.append(row)
                found_data = True

    if found_data:
        return "\n".join(table_lines)

    return raw_text


def chat_with_model(messages, model):

    system_prompt = {
        "role": "system",
        "content": (
            "You are a database assistant.\n"
            "You have access to the following tools:\n"
            "- read_records: Read all students. Arguments: {}\n"
            "- create_student: Create a new student. Arguments: {name: str, email: str, phone_number: str}\n"
            "- update_student: Update a student. Arguments: {student_id: int, name: str, email: str, phone_number: str}\n"
            "- delete_student: Delete a student. Arguments: {student_id: int}\n\n"
            "If you generate a tool call, output ONLY JSON exactly like:\n"
            '{"name":"create_student","arguments":{"name":"John","email":"john@doe.com","phone_number":"123"}}'
        )
    }

    payload = {
        "model": model,
        "messages": [system_prompt] + messages,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    response.raise_for_status()

    data = response.json()
    message = data.get("message", {})
    content = message.get("content", "").strip()

    try:
        import re

        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            clean_content = match.group(0)
            tool_json = json.loads(clean_content)

            if isinstance(tool_json, dict) and "name" in tool_json:
                tool_name = tool_json["name"]
                tool_args = tool_json.get("arguments", {})


                result = run_tool(tool_name, tool_args)


                if tool_name == "read_records":
                    return clean_format(result)
                else:
                    return result

    except Exception as e:

        pass

    return content

if "messages" not in st.session_state:
    st.session_state.messages = []

model = st.sidebar.selectbox("Model", ["qwen2.5-coder:7b"])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Ask anything about database...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            reply = chat_with_model(st.session_state.messages, model)
            st.write(reply)
            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )
        except Exception as e:
            st.error(f"Error: {e}")
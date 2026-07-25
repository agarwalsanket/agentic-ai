
from langchain_core.messages import ToolMessage
from langchain_core.messages import AIMessage

def router(state):
    """
    Detect the 'SEARCH' keyword from the chatbot's message
    """

    content = state["messages"][-1].content.upper()
    if "SEARCH:" in content:
        return "search_node"
    return "__end__"

def handle_human_gate(app, config):
    """
    check if the state is going to be interrupted. In our case the state will be interrupted before Search node.
    """

    # access the current state
    state = app.get_state(config)

    if not state.next:
        return

    if "tools" in state.next:
        # Get the tool calls so we can see what the AI wants to do
        last_message = state.values["messages"][-1]
        tool_call = last_message.tool_calls[0]

        print("\n--- 🛑 AGENT IS PAUSED: Human Approval Required ---")
        user_choice = input("The AI wants to use a tool. Allow? (yes/no/edit): ").lower()
        if user_choice == "yes":
            # Resume by passing None (signals approval)
            for event in app.stream(None, config):
                print(event)
        elif user_choice == "edit":
            new_query = input("Enter a new request: \n")

            edited_tool_call = last_message.tool_calls[0].copy()
            old_query = edited_tool_call["args"]["query"]
            edited_tool_call["args"]["query"] = new_query

            # Inject an explicit Audit Trail into the content string
            # This ensures anyone looking at Langfuse/Opik immediately sees the human intervention
            audit_logged_content = (
                f"{last_message.content}\n\n"
                f"[🔧 SYSTEM NOTE: Tool argument 'query' was manually intercepted and edited "
                f"by a human supervisor from '{old_query}' to '{new_query}']."
            )

            # Update the state with the edited query before resuming
            updated_ai_msg = AIMessage(
                content=audit_logged_content,
                tool_calls=[edited_tool_call],
                id=last_message.id  # Matching the ID triggers an overwrite instead of an append
            )

            # Update state AS IF the tools node just ran
            app.update_state(config, {"messages": [updated_ai_msg]})

            print(f"--- 🔄 Tool arguments updated to: '{new_query}'. Resuming tool node... ---")

            # Resume streaming. The graph will now wake up, execute the 'tools' node,
            # and read your modified query parameter!
            for event in app.stream(None, config):
                print(event)
        else:
            print("--- ❌ Search Vetoed ---")

            # Create a ToolMessage that tells the AI the human said no
            tool_msg = ToolMessage(
                content="Action denied by human supervisor.",
                tool_call_id=tool_call["id"]
            )

            # Update state AS IF the tools node just ran
            app.update_state(config, {"messages": [tool_msg]}, as_node="tools")

            # Now resume; it will go back to the agent to explain the denial
            for event in app.stream(None, config):
                print(event)
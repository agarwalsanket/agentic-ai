

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

    if "search_node" in state.next:
        print("\n--- 🛑 AGENT IS PAUSED: Human Approval Required ---")
        user_choice = input("The AI wants to search the web. Allow? (yes/no/edit): ").lower()
        if user_choice == "yes":
            # Resume by passing None (signals approval)
            for event in app.stream(None, config):
                print(event)
        elif user_choice == "edit":
            new_query = input("Enter a better search query: \n")
            # Update the state with the edited query before resuming
            app.update_state(config, {"messages": [("user", f"SEARCH: {new_query}")]})
            for event in app.stream(None, config):
                print(event)
        else:
            # Veto: Overwrite the message to stop the search trigger
            print("--- ❌ Search Vetoed by Human ---")
            app.update_state(config, {"messages": [("assistant", "Human denied search access.")]})
            for event in app.stream(None, config):
                print(event)
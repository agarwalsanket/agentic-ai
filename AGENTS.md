# Repository Rules for AI Agents
- **Architecture:** LangGraph Pregel logic. Never bypass the `StateGraph` compilation.
- **State Pattern:** Always use `TypedDict`. Avoid Pydantic unless runtime validation is required.
- **Imports:** Use absolute imports (`my_project.nodes`) to prevent circular dependencies.
- **Boundary:** Do not modify the SQLite schema without updating the `SqliteSaver` initialization.

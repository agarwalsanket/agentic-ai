# Modular Stateful Agent with LangGraph & Ollama

This repository demonstrates architecture for stateful AI agents using the Pregel/BSP paradigm. It decouples orchestration from execution through a modular directory structure, ensuring high-scale maintainability and durable persistence.

## 🧠 Principal Narrative: Task-Adaptive Orchestration

Unlike linear chains, this agent utilizes Durable Checkpointing. Every state transition is treated as a Superstep. By persisting snapshots to a local SQLite database, the agent preserves context across independent execution threads, enabling long-horizon task completion without memory loss.

## 🚀 Setup & Usage

### Environment Initialization
```
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate
pip install -r requirements.txt
```

### Security & Performance Flags:
```
bashexport LANGGRAPH_STRICT_MSGPACK=true
```

### Execution
```commandline
python graph.py
```



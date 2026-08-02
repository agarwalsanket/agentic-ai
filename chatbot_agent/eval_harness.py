import asyncio
import os

from dotenv import load_dotenv
from datasets import Dataset
from openai import AsyncOpenAI  # CRITICAL: Switched from OpenAI to AsyncOpenAI
from ragas import experiment, RunConfig
from ragas.metrics.collections import Faithfulness, AnswerRelevancy, AnswerCorrectness
from chatbot_agent.graph import app  # Your compiled LangGraph application
from openai import OpenAI
from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory

load_dotenv()

# Step 1: Define Your Target Test Suite (The Ground Truth Specification)
raw_test_data = {
    "question": [
        "What is the result of 1458 plus 9632?",
        "Who won the most recent formula 1 grand prix race?"
    ],
    "ground_truth": [
        "11090",
        "Search results must provide current 2026 podium data."
    ]
}

raw_test_data2 = [
    {"question": "What is the result of 1458 plus 9632?",
     "ground_truth": "11090"
     },
    {"question": "Who won the most recent formula 1 grand prix race?",
     "ground_truth": "Search results must provide current 2026 podium data."
     }
]

# Step 2: Establish the Local Client Infrastructure & Judgement Factories
local_ollama_client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    timeout=120.0,
    max_retries=3
)

ragas_evaluator_llm = llm_factory(
    model="llama3.1",
    client=local_ollama_client
)

ragas_embeddings = embedding_factory(
    model="nomic-embed-text",
    client=local_ollama_client
)
faithfulness_metric = Faithfulness(llm=llm_factory(model="llama3.1", client=local_ollama_client))

relevancy_metric = AnswerRelevancy(
    llm=ragas_evaluator_llm,
    embeddings=embedding_factory(model="nomic-embed-text", client=local_ollama_client)
)

correctness_metric = AnswerCorrectness(
    llm=ragas_evaluator_llm,
    embeddings=embedding_factory(model="nomic-embed-text", client=local_ollama_client)
)


def run_agent_task_simulation(test_queries):
    """
    Pure synchronous graph simulator
    """

    simulated_agent_metrics = []

    for row in test_queries:
        question = row["question"]
        print(f"-> Invoking Graph for user prompt: '{question}'...")

        # Isolate checkpointer sessions per evaluation trace line
        config = {"configurable": {"thread_id": f"eval_trace_{hash(question) % 10000}"}}
        inputs = {"messages": [("user", question)]}

        # Synchronously execute graph to generate actual trajectories
        state_output = app.invoke(inputs, config)
        print(f"after invoke: {state_output}")
        state = app.get_state(config)
        if "tools" in state.next: # there might have been an interrupt before the tool call
            for event in app.stream(None, config): # Rehydrating/auto-approval for the graph after the interrupt
                print(f"after rehydration: {event}")

        final_state = app.get_state(config) # after the rehydration picking the latest state

        history = final_state.values["messages"]

        final_answer = history[-1].content
        tool_outputs = [
            msg.content for msg in history
            if msg.__class__.__name__ == "ToolMessage"
        ]

        simulated_agent_metrics.append({
        "user_input": question,
        "response": final_answer,
        "retrieved_contexts": tool_outputs,
        "reference": row["ground_truth"]
    })

    return simulated_agent_metrics


@experiment()
async def run_agent_evaluation_step(row ):
    """
    Pure synchronous row-mapper block.
    Executes inputs via standard graph invocation blocks.
    """
    print(f"here 3")
    # # 1. Evaluate Grounding (Is the response supported by tool outputs?)
    faith_result = await faithfulness_metric.ascore(
        user_input=row.get("user_input"),
        response=row.get("response"),
        retrieved_contexts=row.get("retrieved_contexts")
    )

    print(f"here 4")
    relevancy_result = await relevancy_metric.ascore(
        user_input=row.get("user_input"),
        response=row.get("response")
    )

    print(f"here 5")
    correctness_result = await correctness_metric.ascore(
        user_input=row.get("user_input"),
        response=row.get("response"),
        reference=row.get("reference")
    )

    print(f"here 6")

    # Defensive attribute check handling to guarantee data extraction flexibility across minor patches
    f_score = faith_result.value if hasattr(faith_result, "value") else faith_result
    r_score = relevancy_result.value if hasattr(relevancy_result, "value") else relevancy_result
    c_score = correctness_result.value if hasattr(correctness_result, "value") else correctness_result

    print(f"here 7")

    # Return the score properties as key-value pairs for the log output table
    return {
        "faithfulness": f_score,
        "answer_relevancy": r_score,
        "correctness": c_score
    }


def execute_pipeline():
    """
    Pure synchronous graph simulator and evaluator engine
    """
    print("--- 🔬 Step 1: Loading Datasets & Activating Asynchronous Experiment and Evaluation Loop ---")

    simulated_graph_metrics = run_agent_task_simulation(raw_test_data2) # simulate the agent graph to tackle 2 use entries
    evaluation_dataset = Dataset.from_list(simulated_graph_metrics)

    # Execute the asynchronous decorated function directly
    print("\nExecuting LLM-as-a-Judge grading matrices and compiling logs...")
    experiment_results = []
    for row in evaluation_dataset:
        print(f"here 1")
        experiment_result = asyncio.run(run_agent_evaluation_step(row=row))
        print(f"here 2")
        experiment_results.append(experiment_result)


    print("\n============== 📊 EVALUATION EXPERIMENT SUMMARY ==============")
    print(experiment_results)
    print("===========================================================")


if __name__ == "__main__":
    execute_pipeline()

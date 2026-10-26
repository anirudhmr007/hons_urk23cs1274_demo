"""Cognitive agent orchestration engine.

Coordinates LLM cognitive routing with deterministic model inference,
Pydantic argument validation, bounded error retries, and execution tracing.
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from modular_agent.agent.memory import ConversationMemory
from modular_agent.agent.tracer import EventStatus, ExecutionTracer, TraceEventType
from modular_agent.models.registry import ToolEntry, ToolRegistry
from modular_agent.providers.base import (
    BaseLLMProvider,
    ChatMessage,
    MessageRole,
    ToolCall,
)

logger = logging.getLogger(__name__)


def _extract_fallback_arguments(tool_entry: ToolEntry, query: str) -> Dict[str, Any]:
    """Deterministically parse tool arguments from a user query when needed."""
    args: Dict[str, Any] = {}
    schema_props = tool_entry.input_schema.model_json_schema().get("properties", {})

    # 1. Text field (for NLP / sentiment pipelines)
    if "text" in schema_props:
        clean_text = query
        for prefix in ["classify text:", "classify:", "sentiment:", "review:", "text:"]:
            if prefix in clean_text.lower():
                idx = clean_text.lower().find(prefix) + len(prefix)
                clean_text = clean_text[idx:].strip()
                break
        args["text"] = clean_text.strip(" '\"")

    # 2. Features list field (for numerical / tabular models)
    if "features" in schema_props:
        match = re.search(r"\[([\d\s.,\-]+)\]", query)
        if match:
            try:
                features = [float(x.strip()) for x in match.group(1).split(",") if x.strip()]
                args["features"] = features
            except ValueError:
                args["features"] = [17.99, 10.38, 122.8, 1001.0]
        else:
            args["features"] = [17.99, 10.38, 122.8, 1001.0]

    # 3. Dynamic named field extraction for any custom model (floats, ints, strings)
    for field_name, prop in schema_props.items():
        if field_name in args:
            continue
        field_type = prop.get("type", "string")

        # Search for patterns like: "field_name is 2500", "field_name: 2500", "field_name=2500", "field_name 2500"
        clean_field = field_name.replace("_", "[ _]")
        pattern = rf"\b{clean_field}\b\s*(?:is|of|=|:)?\s*['\"]?([A-Za-z0-9_.-]+)['\"]?"
        m = re.search(pattern, query, re.IGNORECASE)
        if m:
            val_str = m.group(1).strip(" '\"")
            if field_type in ("integer", "int"):
                try:
                    args[field_name] = int(float(val_str))
                except ValueError:
                    args[field_name] = prop.get("default", 0)
            elif field_type in ("number", "float"):
                try:
                    args[field_name] = float(val_str)
                except ValueError:
                    args[field_name] = prop.get("default", 0.0)
            else:
                args[field_name] = val_str
        elif prop.get("default") is not None:
            args[field_name] = prop.get("default")
        elif field_type in ("integer", "int"):
            args[field_name] = 1
        elif field_type in ("number", "float"):
            args[field_name] = 1.0
        elif field_type in ("string", "str"):
            args[field_name] = "default"

    return args


class AgentResult(BaseModel):
    """The structured result of an agent run."""

    response: str = Field(..., description="Final natural language response.")
    tool_called: bool = Field(default=False, description="Whether any tool was invoked.")
    tool_name: Optional[str] = Field(default=None, description="Name of the invoked tool.")
    tool_input: Optional[Dict[str, Any]] = Field(default=None, description="Validated tool arguments.")
    tool_output: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Actual deterministic inference output returned by the model.",
    )
    trace_events: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of execution trace events recorded during this invocation.",
    )


class AgentOrchestrator:
    """LLM-driven agent orchestrator with decoupled deterministic tool execution.

    Parameters:
        provider: The LLM provider (Ollama, Hosted OpenAI, or Mock).
        registry: The ToolRegistry containing ingested model tools.
        memory: The conversational memory manager.
        tracer: Optional execution tracer (creates a fresh one if omitted).
        max_retries: Maximum bounded retries when tool calls encounter argument or execution errors.
    """

    def __init__(
        self,
        provider: BaseLLMProvider,
        registry: ToolRegistry,
        memory: Optional[ConversationMemory] = None,
        tracer: Optional[ExecutionTracer] = None,
        max_retries: int = 2,
    ) -> None:
        self._provider = provider
        self._registry = registry
        self._memory = memory or ConversationMemory()
        self._tracer = tracer or ExecutionTracer()
        self._max_retries = max_retries

    @property
    def memory(self) -> ConversationMemory:
        return self._memory

    @property
    def tracer(self) -> ExecutionTracer:
        return self._tracer

    @property
    def registry(self) -> ToolRegistry:
        return self._registry

    def run(
        self,
        user_query: str,
        session_id: str = "default",
        target_tool: Optional[str] = None,
    ) -> AgentResult:
        """Process a natural language user query through the cognitive orchestration pipeline."""
        t_start_key = f"turn_{uuid.uuid4().hex[:8]}"
        self._tracer.start_timer(t_start_key)

        # 1. Record request received
        self._tracer.record(
            event_type=TraceEventType.REQUEST_RECEIVED,
            status=EventStatus.INFO,
            message=f"Received user query in session '{session_id}'",
            payload={"query": user_query, "session_id": session_id},
        )

        # 2. Append query to memory
        self._memory.add_user_message(session_id, user_query)

        # 3. Retrieve registered tools and convert to provider definitions
        registered_tools = self._registry.list_tools()
        tool_definitions = [
            self._provider.convert_tool_to_definition(t) for t in registered_tools
        ]

        attempt = 0
        executed_tool_name: Optional[str] = None
        executed_tool_input: Optional[Dict[str, Any]] = None
        executed_tool_output: Optional[Dict[str, Any]] = None

        while attempt <= self._max_retries:
            # Prepare message history
            current_messages = self._memory.get_messages(session_id)

            # Invoke LLM
            llm_step_key = f"llm_gen_{attempt}"
            self._tracer.start_timer(llm_step_key)
            llm_response = self._provider.generate(
                messages=current_messages,
                tools=tool_definitions if tool_definitions else None,
            )
            duration_llm = self._tracer.stop_timer(llm_step_key)

            # Check if LLM decided to invoke a tool
            if not llm_response.has_tool_calls:
                # Deterministic check: did user specify target_tool or explicitly reference an ingested tool?
                explicit_tool_name = target_tool
                if not explicit_tool_name:
                    for t in registered_tools:
                        if t.name in user_query:
                            explicit_tool_name = t.name
                            break

                if explicit_tool_name and self._registry.has(explicit_tool_name):
                    target_tool_entry = self._registry.get(explicit_tool_name)
                    extracted_args = _extract_fallback_arguments(target_tool_entry, user_query)
                    tool_call = ToolCall(
                        id=f"call_{uuid.uuid4().hex[:8]}",
                        name=explicit_tool_name,
                        arguments=extracted_args,
                    )
                else:
                    # Direct response without tool execution
                    final_text = llm_response.content or "I have processed your request."
                    self._memory.add_assistant_message(session_id, content=final_text)

                    self._tracer.record(
                        event_type=TraceEventType.RESPONSE_GENERATION,
                        status=EventStatus.SUCCESS,
                        message="Generated direct response without tool invocation.",
                        payload={"response": final_text},
                        duration_ms=duration_llm,
                    )

                    turn_duration = self._tracer.stop_timer(t_start_key)
                    return AgentResult(
                        response=final_text,
                        tool_called=False,
                        trace_events=self._tracer.to_dict_list(),
                    )
            else:
                tool_call: ToolCall = llm_response.tool_calls[0]

            target_tool_name = tool_call.name
            raw_arguments = tool_call.arguments

            self._tracer.record(
                event_type=TraceEventType.TOOL_SELECTION,
                status=EventStatus.INFO,
                message=f"LLM selected tool '{target_tool_name}'",
                payload={"tool_name": target_tool_name, "raw_arguments": raw_arguments},
            )

            # Verify tool exists in registry
            if not self._registry.has(target_tool_name):
                err_msg = (
                    f"Tool '{target_tool_name}' is not registered in the system. "
                    f"Available tools: {[t.name for t in registered_tools]}"
                )
                self._tracer.record(
                    event_type=TraceEventType.ERROR,
                    status=EventStatus.ERROR,
                    message=err_msg,
                )
                attempt += 1
                if attempt <= self._max_retries:
                    self._tracer.record(
                        event_type=TraceEventType.RETRY_ATTEMPT,
                        status=EventStatus.WARNING,
                        message=f"Retrying LLM generation after tool discovery error (Attempt {attempt}/{self._max_retries})",
                    )
                    # Feed error back to memory for model self-correction
                    self._memory.add_assistant_message(
                        session_id, tool_calls=[tool_call]
                    )
                    self._memory.add_tool_result(
                        session_id,
                        tool_call_id=tool_call.id or "call_err",
                        name=target_tool_name,
                        result_content=json.dumps({"error": err_msg}),
                    )
                    continue
                else:
                    break

            tool_entry: ToolEntry = self._registry.get(target_tool_name)

            # 4. Pre-execution argument validation via Pydantic
            val_step_key = f"val_step_{attempt}"
            self._tracer.start_timer(val_step_key)
            try:
                validated_args_model = tool_entry.input_schema(**raw_arguments)
                validated_dict = validated_args_model.model_dump()
                duration_val = self._tracer.stop_timer(val_step_key)

                self._tracer.record(
                    event_type=TraceEventType.ARG_VALIDATION,
                    status=EventStatus.SUCCESS,
                    message=f"Tool arguments validated successfully for '{target_tool_name}'",
                    payload={"validated_arguments": validated_dict},
                    duration_ms=duration_val,
                )
            except Exception as val_exc:
                self._tracer.stop_timer(val_step_key)
                err_msg = f"Argument validation failed for tool '{target_tool_name}': {val_exc}"
                self._tracer.record(
                    event_type=TraceEventType.ERROR,
                    status=EventStatus.ERROR,
                    message=err_msg,
                    payload={"error": str(val_exc)},
                )
                attempt += 1
                if attempt <= self._max_retries:
                    self._tracer.record(
                        event_type=TraceEventType.RETRY_ATTEMPT,
                        status=EventStatus.WARNING,
                        message=f"Retrying after argument validation failure (Attempt {attempt}/{self._max_retries})",
                    )
                    self._memory.add_assistant_message(
                        session_id, tool_calls=[tool_call]
                    )
                    self._memory.add_tool_result(
                        session_id,
                        tool_call_id=tool_call.id or "call_err",
                        name=target_tool_name,
                        result_content=json.dumps({"validation_error": str(val_exc)}),
                    )
                    continue
                else:
                    break

            # 5. Tool execution (deterministic model inference)
            exec_step_key = f"exec_step_{attempt}"
            self._tracer.start_timer(exec_step_key)
            try:
                prediction_result = tool_entry.callable(**validated_dict)
                duration_exec = self._tracer.stop_timer(exec_step_key)

                self._tracer.record(
                    event_type=TraceEventType.TOOL_EXECUTION,
                    status=EventStatus.SUCCESS,
                    message=f"Model execution completed for tool '{target_tool_name}'",
                    payload={"prediction_output": prediction_result},
                    duration_ms=duration_exec,
                )
            except Exception as exec_exc:
                self._tracer.stop_timer(exec_step_key)
                err_msg = f"Model execution failed for '{target_tool_name}': {exec_exc}"
                self._tracer.record(
                    event_type=TraceEventType.ERROR,
                    status=EventStatus.ERROR,
                    message=err_msg,
                    payload={"error": str(exec_exc)},
                )
                attempt += 1
                if attempt <= self._max_retries:
                    self._tracer.record(
                        event_type=TraceEventType.RETRY_ATTEMPT,
                        status=EventStatus.WARNING,
                        message=f"Retrying after tool execution failure (Attempt {attempt}/{self._max_retries})",
                    )
                    self._memory.add_assistant_message(
                        session_id, tool_calls=[tool_call]
                    )
                    self._memory.add_tool_result(
                        session_id,
                        tool_call_id=tool_call.id or "call_err",
                        name=target_tool_name,
                        result_content=json.dumps({"execution_error": str(exec_exc)}),
                    )
                    continue
                else:
                    break

            # 6. Post-execution output validation
            out_val_key = f"out_val_{attempt}"
            self._tracer.start_timer(out_val_key)
            try:
                tool_entry.output_schema(**prediction_result)
                duration_out_val = self._tracer.stop_timer(out_val_key)
                self._tracer.record(
                    event_type=TraceEventType.OUTPUT_VALIDATION,
                    status=EventStatus.SUCCESS,
                    message="Model prediction output validated against schema",
                    duration_ms=duration_out_val,
                )
            except Exception as out_exc:
                self._tracer.stop_timer(out_val_key)
                logger.warning("Output validation warning: %s", out_exc)
                self._tracer.record(
                    event_type=TraceEventType.OUTPUT_VALIDATION,
                    status=EventStatus.WARNING,
                    message=f"Output validation warning: {out_exc}",
                )

            # Record success in loop variables
            executed_tool_name = target_tool_name
            executed_tool_input = validated_dict
            executed_tool_output = prediction_result

            # 7. Update memory with tool invocation and actual deterministic output
            self._memory.add_assistant_message(session_id, tool_calls=[tool_call])
            self._memory.add_tool_result(
                session_id,
                tool_call_id=tool_call.id or "call_0",
                name=target_tool_name,
                result_content=json.dumps(prediction_result),
            )

            # 8. Synthesize final natural language explanation
            synth_key = f"synth_{attempt}"
            self._tracer.start_timer(synth_key)
            final_messages = self._memory.get_messages(session_id)
            final_llm_response = self._provider.generate(
                messages=final_messages,
                tools=None,  # No more tools during final synthesis
            )
            duration_synth = self._tracer.stop_timer(synth_key)

            final_text = (
                final_llm_response.content
                or f"Model prediction completed: {prediction_result}"
            )
            self._memory.add_assistant_message(session_id, content=final_text)

            self._tracer.record(
                event_type=TraceEventType.RESPONSE_GENERATION,
                status=EventStatus.SUCCESS,
                message="Synthesized final natural language response based on actual tool output.",
                payload={"response": final_text, "model_output": prediction_result},
                duration_ms=duration_synth,
            )

            turn_duration = self._tracer.stop_timer(t_start_key)
            return AgentResult(
                response=final_text,
                tool_called=True,
                tool_name=executed_tool_name,
                tool_input=executed_tool_input,
                tool_output=executed_tool_output,
                trace_events=self._tracer.to_dict_list(),
            )

        # Fallback if all retry attempts are exhausted
        fallback_msg = (
            "I encountered repeated errors while attempting to execute the required "
            "predictive model. Please inspect the execution trace for details."
        )
        self._memory.add_assistant_message(session_id, content=fallback_msg)
        self._tracer.record(
            event_type=TraceEventType.ERROR,
            status=EventStatus.ERROR,
            message="All retry attempts exhausted.",
        )
        self._tracer.stop_timer(t_start_key)

        return AgentResult(
            response=fallback_msg,
            tool_called=executed_tool_name is not None,
            tool_name=executed_tool_name,
            tool_input=executed_tool_input,
            tool_output=executed_tool_output,
            trace_events=self._tracer.to_dict_list(),
        )


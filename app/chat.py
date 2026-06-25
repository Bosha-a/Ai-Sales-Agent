import asyncio
import time
import streamlit as st
from bson.objectid import ObjectId


def render_chat_page(agent, deps, save_turn, rename_session, dir_class, esc,
                     log_usage, approximate_tokens, calculate_cost, SYSTEM_PROMPT,
                     assistant_avatar=None):
    """Chat page — AI sales agent interface."""

    st.title("Kayfa Agent")
    sid = st.session_state.current_session
    chat_messages = st.session_state.sessions[sid]["messages"]

    for msg in chat_messages:
        avatar = assistant_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            cls = dir_class(msg["content"])
            st.markdown(f'<div class="{cls}">{esc(msg["content"])}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Ask me anything about Kayfa's courses, tracks, and diplomas..."):
        message_id = str(ObjectId())
        st.session_state.current_message_id = message_id
        chat_messages.append({"role": "user", "content": prompt})
        save_turn(sid, "user", prompt)
        with st.chat_message("user"):
            cls = dir_class(prompt)
            st.markdown(f'<div class="{cls}">{esc(prompt)}</div>', unsafe_allow_html=True)
        with st.chat_message("assistant", avatar=assistant_avatar):
            with st.spinner("Kayfa AI is thinking..."):
                start_time = time.time()
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None
                if loop and loop.is_running():
                    import nest_asyncio
                    nest_asyncio.apply()
                    model_history = st.session_state.sessions[sid].get("model_history", [])
                    result = loop.run_until_complete(agent.run(prompt, deps=deps, message_history=model_history))
                else:
                    model_history = st.session_state.sessions[sid].get("model_history", [])
                    result = asyncio.run(agent.run(prompt, deps=deps, message_history=model_history))
                latency_ms = int((time.time() - start_time) * 1000)
            
            # Log usage for monitoring
            try:
                usage = result.usage()
                input_tokens = usage.input_tokens
                output_tokens = usage.output_tokens
            except Exception:
                input_tokens = output_tokens = 0

            full_history_text = "\n".join(
                f"{msg.get('role', '')}: {msg.get('content', '')}" for msg in chat_messages
            )
            baseline_input_tokens = approximate_tokens(SYSTEM_PROMPT) + approximate_tokens(full_history_text)
            baseline_cost = calculate_cost("groq", "openai/gpt-oss-20b", baseline_input_tokens, output_tokens)
            
            # Extract tool calls from result
            tool_calls = []
            tool_results = []
            try:
                for msg in result.all_messages():
                    if hasattr(msg, 'parts'):
                        for part in msg.parts:
                            if hasattr(part, 'tool_name'):
                                tool_calls.append({
                                    "tool": part.tool_name,
                                    "args": getattr(part, 'args', {})
                                })
                            if hasattr(part, 'tool_name') and hasattr(part, 'result'):
                                tool_results.append({
                                    "tool": part.tool_name,
                                    "result": str(part.result)[:500]
                                })
            except Exception:
                pass
            
            # Log the LLM call
            current_user = st.session_state.get("user", {})
            log_usage(
                conversation_id=sid,
                user_id=current_user.get("id") or current_user.get("username", "unknown"),
                username=current_user.get("name", "unknown"),
                model_provider="groq",
                model_name="openai/gpt-oss-20b",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                tool_calls=tool_calls,
                tool_results=tool_results,
                latency_ms=latency_ms,
                step_type="llm_call",
                message_id=message_id,
                trace_data={
                    "prompt": prompt,
                    "reasoning_summary": "Classify the user's intent, retrieve Kayfa knowledge when needed, answer from sources, and capture a lead only after confirmed buying signals plus name and phone.",
                    "response": result.output,
                    "tool_calls": tool_calls,
                    "tool_results": tool_results,
                    "optimization": {
                        "applied_fix": "Capped pydantic-ai message_history to the latest five model messages.",
                        "baseline_input_tokens_no_history_cap": baseline_input_tokens,
                        "actual_input_tokens": input_tokens,
                        "saved_input_tokens_estimate": max(0, baseline_input_tokens - input_tokens),
                        "baseline_cost_usd_no_history_cap": baseline_cost,
                        "actual_cost_usd": calculate_cost("groq", "openai/gpt-oss-20b", input_tokens, output_tokens),
                    },
                }
            )
            st.session_state.pop("current_message_id", None)
            
            st.session_state.sessions[sid]["model_history"] = result.all_messages()[-5:]
            cls = dir_class(result.output)
            st.markdown(f'<div class="{cls}">{esc(result.output)}</div>', unsafe_allow_html=True)
        chat_messages.append({"role": "assistant", "content": result.output})
        save_turn(sid, "assistant", result.output)
        sdata = st.session_state.sessions[sid]
        if sdata["name"] in ("New Chat", "Session 1"):
            new_name = prompt[:40] + ("..." if len(prompt) > 40 else "")
            sdata["name"] = new_name
            rename_session(sid, new_name)

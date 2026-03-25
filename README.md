# open-webui-mistral-filter
This filter function exposes Mistral AI Chat Completions API reasoning in the response stream by wrapping thinking output in <think> tags. It can also append a configurable reminder to user messages at a chosen interval, helping reinforce system instructions during longer conversations. Useful for debugging, experimentation, and workflows where you want Mistral’s thinking phase to be visible in real time.

# Installation
## Automatic install
Go to https://openwebui.com/posts/mistral_ai_chat_completions_api_thinking_filter_dea9d2fe

## Manual install
1. Open `Admin Panel`
2. Select `Functions` tab
3. Click `+ New Function` button
4. Copy & paste `mistral_think_filter.py` contents into the code block.
5. Save

If you have trouble enabling the filter function. Help can be found here https://docs.openwebui.com/

# Known Problems
Tasks do not function correctly with the Mistral reasoning models (title-, tag generation etc.). The fix for this is set the task model to a non-reasoning model.

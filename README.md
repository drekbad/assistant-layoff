# assistant-layoff #
#### Fire all your OpenAI Assistant API assistants... Maybe you ALSO mistakenly created 822 assistants.
<div style="text-align:center">![assistant](https://cdn4.whatculture.com/images/2021/04/5e0ece585db5a418-600x338.jpg)</div>
---
After accidentally making 822 OpenAI Assistant API assistants, I realized I misinterpreted the intended assistant creation and management incorrectly.
Since OpenAI has not provided a better way to manage assistants, you may only remove them through the app UI individually.

---
This script requests your authorization token, easily retrieved via request headers with an authenticated OpenAI session.
It will find all assistants and group them by their name, giving a readout of all the names and their counts.
Delete by name or delete all at once. The progress will be indicated by 25 percent increments until done.

---
### Usage:
python script_name.py [options]
Options:
    --no-throttle, -nt    Disable throttling between requests.

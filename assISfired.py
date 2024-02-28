import requests
import time
import sys
import json

# Define headers globally since they are used multiple times
GLOBAL_HEADERS = {}

def graceful_exit():
    print("\nExiting program...")
    sys.exit()

def print_help_menu():
    help_text = """
OpenAI Assistant Deletion Tool:
This script allows you to fetch and delete OpenAI Assistants.

Usage:
    python script_name.py [options]

Options:
    --no-throttle, -nt    Disable throttling between requests.
    --help, -h            Display this help menu.

Example:
    python script_name.py --no-throttle
    """
    print(help_text)
    sys.exit()

def fetch_assistants():
    url = 'https://api.openai.com/v1/assistants'
    params = {'limit': 100}
    assistants = {}
    has_more = True
    last_id = None

    while has_more:
        if last_id:
            params['after'] = last_id
        response = requests.get(url, headers=GLOBAL_HEADERS, params=params)
        if response.status_code == 200:
            data = response.json()
            for assistant in data['data']:
                name = assistant['name']
                if name not in assistants:
                    assistants[name] = []
                assistants[name].append(assistant['id'])
            last_id = data['data'][-1]['id'] if data['data'] else None
            has_more = data['has_more']
            print(f"Successfully fetched {len(data['data'])} assistants")
        else:
            print(f"Failed to fetch assistants: {response.status_code}")
            break  # Exit the fetching loop on failure
        if throttle:  # Check global throttle flag
            time.sleep(1)  # Basic throttling
    print()  # Add line break after the last successfully fetched message
    return assistants

def print_totals_per_name(assistants):
    total_assistants = sum(len(ids) for ids in assistants.values())
    for name, ids in sorted(assistants.items()):
        print(f"TOTAL assistants for {name}: {len(ids)}")
    print(f"\nTOTAL assistants: {total_assistants}\n")

def delete_assistants(assistants_to_delete):
    deleted_count = 0
    total = len(assistants_to_delete)

    for index, assistant_id in enumerate(assistants_to_delete, start=1):
        delete_response = requests.delete(f'https://api.openai.com/v1/assistants/{assistant_id}', headers=GLOBAL_HEADERS)
        if delete_response.status_code in [200, 204] and delete_response.json().get("deleted", False):
            deleted_count += 1
        else:
            print(f"Failed to delete assistant {assistant_id}: {delete_response.status_code}, {delete_response.text}")

        # Update progress only for 25%, 50%, 75%, not for 100%
        if total > 1 and index in [int(total * 0.25), int(total * 0.5), int(total * 0.75)]:
            print(f"{int((index/total) * 100)}% deleted...")

    print(f"Deletion completed: {deleted_count}/{total} assistants deleted.")

def confirm_action(prompt):
    while True:
        choice = input(prompt).strip().lower()
        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False

# Check for system arguments
throttle = True
if len(sys.argv) > 1:
    if '--no-throttle' in sys.argv or '-nt' in sys.argv:
        throttle = False
    if '--help' in sys.argv or '-h' in sys.argv:
        print_help_menu()

try:
    raw_token = input("Please enter your authorization token (format: Bearer YOUR_TOKEN_HERE or sess-YOUR_TOKEN_PART):\n")
    print()  # Add line break after the input of the auth token
    if raw_token.strip().lower() in ['q', 'quit', 'exit']:
        graceful_exit()
    auth_token = f"Bearer {raw_token.split()[-1]}"
    GLOBAL_HEADERS.update({
        'Authorization': auth_token,
        'Content-Type': 'application/json',
        'OpenAI-Beta': 'assistants=v1'
    })

    # Main loop to fetch, display, and delete assistants
    while True:
        assistants = fetch_assistants()
        if not assistants:
            break  # Exit if no assistants were fetched after displaying the message

        print_totals_per_name(assistants)

        delete_choice = input("Enter the exact name of the assistant type to delete, 'ALL' to delete all, or 'q' to quit:\n")
        if delete_choice.lower() in ['q', 'quit', 'exit']:
            graceful_exit()

        delete_all = delete_choice == 'ALL'
        assistants_to_delete = sum(assistants.values(), []) if delete_all else assistants.get(delete_choice, [])
        
        if not assistants_to_delete:
            print("Invalid choice. Please enter a valid assistant name or 'ALL'.")
            continue
        
        confirmation = confirm_action(f"Are you sure you want to delete {'all ' if delete_all else ''}{len(assistants_to_delete)} {'assistants' if delete_all or not assistants_to_delete else delete_choice + ' assistants'}? (y/n):\n")
        if confirmation:
            delete_assistants(assistants_to_delete)
        
        rerun = confirm_action("Check new assistant count? (y/n):\n")
        if not rerun:
            break

except KeyboardInterrupt:
    graceful_exit()

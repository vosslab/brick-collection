#!/usr/bin/env python3

import os
import sys

# Get the directory name of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
# Add the parent directory to sys.path
sys.path.append(parent_dir)
# Now you can import the module
import bricklink_wrapper

def ask_yes_no(question, default="no"):
    while True:
        answer = input(f"{question} (y/n) [default: {default}]: ").strip().lower()
        if len(answer) == 0:
            return default == "yes"
        answer = answer[0]
        if answer in ["y", "n"]:
            return answer == "y"
        print("Please enter 'y' or 'n'.")
        sys.exit(1)

stages_of_build = [
    'completely disassembled',
    'mostly disassembled',
    'half-built',
    'partially assembled',
    'almost fully constructed',
]

included_or_not = {
    'minifigs': None,
    'instructions': None,
    'box': None,
    'extra pieces': None,
    'minifigs': None,
}

def main():
    # Generating description
    description = []

    # 1. Percent complete
    percent_complete = int(input("Percent complete (e.g., 95): ").strip())
    # 5. Has extra pieces (if percent complete > 99)
    if percent_complete < 99:
        included_or_not['extra pieces'] = False

    for key in included_or_not.keys():
        if included_or_not[key] is not None:
            continue
        result = ask_yes_no(f"does set have {key}", default="no")
        included_or_not[key] = result

    # 6. Personal collection, bought by you
    personal_collection = ask_yes_no("Personal collection, bought by you")
    # Personal collection
    if personal_collection:
        description.append("📦 From personal collection, bought by me")

    # Create a dictionary for quick lookup
    build_status_dict = {status[0]: status for status in stages_of_build}

    # Generate the input prompt dynamically
    input_prompt = "Build status "
    for key, value in build_status_dict.items():
        input_prompt += f"\n\t({key}){value[1:]}, "

    # Remove the trailing comma and space
    input_prompt = input_prompt.rstrip(", ") + ": "

    # User prompt for build status
    build_status_input = input(input_prompt).strip().lower()[0]

    # Get the corresponding status from the dictionary
    build_status = build_status_dict.get(build_status_input, 'Unknown')

    # Output the selected build status
    print(f"Selected build status: {build_status}")

    # Build status
    if build_status != 'Unknown':
        description.append(f"{build_status} and stored in plastic bag")
    else:
        description.append(f"stored in plastic bag")

    # Percent complete
    if percent_complete < 100:
        percent_description = f"Visual check shows {percent_complete}% complete"
        if percent_complete < 99:
            percent_description += " and priced accordingly"
        description.append(percent_description)
    else:
        description.append(f'{percent_complete}% complete')

    #positives
    positive_text = ''
    positive_text += "✅ "
    for key, value in included_or_not.items():
        if value is True:
            positive_text += f"includes {key}; "
    positive_text = positive_text[:-2]
    description.append(positive_text)

    #negatives
    negative_text = ''
    negative_text += "❌ "
    for key, value in included_or_not.items():
        if value is False:
            negative_text += f"no {key}; "
    negative_text = negative_text[:-2]
    description.append(negative_text)

    # Output the generated description
    final_description = "; ".join(description)
    print("\nGenerated Description:")
    print(final_description)

if __name__ == "__main__":
    main()

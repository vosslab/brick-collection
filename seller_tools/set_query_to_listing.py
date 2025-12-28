#!/usr/bin/env python3

import os
import sys

# Add parent directory to sys.path for importing custom modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

# Import custom module from parent directory
import libbrick
import libbrick.wrappers.bricklink_wrapper as bricklink_wrapper

def ask_yes_no(question, default="no"):
    """Prompt a yes/no question to the user with a default answer."""
    while True:
        answer = input(f"{question} (y/n) [default: {default}]: ").strip().lower()
        if not answer:
            return default == "yes"
        if answer[0] in ["y", "n"]:
            return answer[0] == "y"
        print("Please enter 'y' or 'n'.")

def get_percent_complete():
    """Prompt the user to enter the percent complete of the set."""
    return int(input("Percent complete (e.g., 95): ").strip())

def get_included_items(included_or_not):
    """Prompt the user to confirm if specific items are included."""
    for key in included_or_not.keys():
        if included_or_not[key] is not None:
            continue
        included_or_not[key] = ask_yes_no(f"Does set have {key}?", default="no")
    return included_or_not

def get_personal_collection():
    """Prompt the user to confirm if the set is from a personal collection."""
    return ask_yes_no("Personal collection, bought by you")

def get_build_status(stages_of_build):
    """Prompt the user to select the build status from a list."""
    build_status_dict = {status[0]: status for status in stages_of_build}
    input_prompt = "Build status:\n" + "".join(
        [f"\t({key}){value}\n" for key, value in build_status_dict.items()]
    ) + "Please select: "
    build_status_input = input(input_prompt).strip().lower()
    return build_status_dict.get(build_status_input, 'Unknown')

def generate_description(included_or_not, percent_complete, build_status, personal_collection):
    """Generate the final description based on the provided details."""
    description = []

    if build_status != 'Unknown':
        description.append(f"{build_status} and stored in plastic bag")
    else:
        description.append("stored in plastic bag")

    if percent_complete < 100:
        percent_description = f"Visual inspection {percent_complete}% complete"
        if percent_complete < 99:
            percent_description += " and priced accordingly"
        description.append(percent_description)
    else:
        description.append(f'{percent_complete}% complete')

    if personal_collection:
        description.append("📦 From personal collection, bought by me")

    if included_or_not['minifigs'] == 'none':
        description.append("set has no minifigs")

    # Generate list of included items
    positive_text = "✅ "
    for key, value in included_or_not.items():
        if value is True:
            positive_text += f"includes {key}; "
    if len(positive_text) > 2:
        positive_text = positive_text[:-2]  # Remove trailing semicolon and space
        description.append(positive_text)

    # Generate list of excluded items
    negative_text = "❌ "
    for key, value in included_or_not.items():
        if value is False:
            negative_text += f"no {key}; "
    if len(negative_text) > 2:
        negative_text = negative_text[:-2]  # Remove trailing semicolon and space
        description.append(negative_text)

    return "; ".join(description)

def listing_to_stdout(listing_dict):
    print("")
    import pprint
    pprint.pprint(listing_dict)
    print(listing_dict.keys())
    return

def main():
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
    }

    # Gather information
    setID = libbrick.user_input_set_id()
    print(f"Set ID: {setID}")
    BLW = bricklink_wrapper.BrickLink()

    sold_data = BLW.getSetPriceDetails(setID, guide_type='sold', new_or_used='U')
    #listing_to_stdout(sold_data)
    #print(sold_data['item'])
    for i in sold_data['price_detail']:
        listing_to_stdout(i)

    stock_data = BLW.getSetPriceDetails(setID, guide_type='stock', new_or_used='U')
    for i in stock_data['price_detail']:
        listing_to_stdout(i)

    print("")
    percent_complete = get_percent_complete()
    if percent_complete < 99:
        included_or_not['extra pieces'] = False
    print("")
    minifigs = BLW.getMinifigIDsFromSet(setID)
    minifig_count = len(minifigs)
    if minifig_count == 0:
        included_or_not['minifigs'] = 'none'
    print("")
    included_or_not = get_included_items(included_or_not)
    print("")
    personal_collection = get_personal_collection()
    print("")
    build_status = get_build_status(stages_of_build)

    # Generate and output the description
    final_description = generate_description(
        included_or_not, percent_complete, build_status, personal_collection
    )
    print("\nGenerated Description:")
    print(final_description)

if __name__ == "__main__":
    main()

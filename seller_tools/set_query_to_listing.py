#!/usr/bin/env python3

def ask_yes_no(question, default="no"):
    while True:
        answer = input(f"{question} (y/n) [default: {default}]: ").strip().lower()
        if answer in ["y", "n"]:
            return answer == "y"
        elif answer == "":
            return default == "yes"
        print("Please enter 'y' or 'n'.")

def main():
    # 1. Percent complete
    percent_complete = int(input("Percent complete (e.g., 95): ").strip())
    
    # 2. Has minifigs (default: no)
    has_minifigs = ask_yes_no("Has minifigs", default="no")
    
    # 3. Has instructions
    has_instructions = ask_yes_no("Has instructions")
    
    # 4. Has box
    has_box = ask_yes_no("Has box")
    
    # 5. Has extra pieces (if percent complete > 99)
    has_extra_pieces = False
    if percent_complete > 99:
        has_extra_pieces = ask_yes_no("Has extra pieces")
    
    # 6. Personal collection, bought by you
    personal_collection = ask_yes_no("Personal collection, bought by you")
    
    # 7. Build status
    build_status = input("Build status (d)isassembled, (p)artially built, (b)uilt: ").strip().lower()
    build_status_dict = {'d': 'Disassembled', 'p': 'Partially built', 'b': 'Built'}
    build_status = build_status_dict.get(build_status, 'Unknown')

    # Generating description
    description = []

    # Build status
    if build_status != 'Unknown':
        description.append(f"{build_status} and stored in plastic bag")
    
    # Percent complete
    if percent_complete < 100:
        description.append(f"Visual inspection {percent_complete}% complete")
        if percent_complete < 99:
            description.append("and priced accordingly")
    
    # Instructions, Minifigs, Box
    if has_instructions:
        description.append("✅ Includes instructions")
    if has_minifigs:
        description.append("✅ Includes minifigs")
    else:
        description.append("❌ No minifigs")
    if has_box:
        description.append("✅ Includes box")
    
    # Extra pieces
    if has_extra_pieces:
        description.append("✅ Includes extra pieces")
    
    # Personal collection
    if personal_collection:
        description.append("📦 From personal collection, bought by me")

    # Output the generated description
    final_description = "; ".join(description)
    print("\nGenerated Description:")
    print(final_description)

if __name__ == "__main__":
    main()

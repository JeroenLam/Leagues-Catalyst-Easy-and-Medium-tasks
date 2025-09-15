#!/usr/bin/env python3
import json
from collections import Counter

# Load the JSON file
with open('catalyst_league_tasks.json', 'r') as f:
    data = json.load(f)

# Extract all tags
all_tags = []
for task in data['tasks']:
    if 'Tags' in task:
        all_tags.extend(task['Tags'])

# Count unique tags
tag_counts = Counter(all_tags)

print("UNIQUE TAGS FOUND:")
print("=" * 50)
for tag, count in sorted(tag_counts.items()):
    print(f"{tag:<20} : {count:>4} times")

print(f"\nTotal unique tags: {len(tag_counts)}")
print(f"Total tag instances: {sum(tag_counts.values())}")

# Show some example tasks with their tags
print(f"\nSAMPLE TASKS WITH TAGS:")
print("=" * 50)
for i, task in enumerate(data['tasks'][:10]):
    print(f"{i+1}. {task['Task'][:60]}...")
    print(f"   Tags: {task.get('Tags', [])}")
    print(f"   Pts: {task.get('Pts')}")
    print()
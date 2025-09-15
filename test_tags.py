#!/usr/bin/env python3
"""
Test script to verify the updated tag generation logic.
"""
import json
import sys
import os

# Add the current directory to the path to import the scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from catalyst_league_scraper import CatalystLeagueScraper

def test_tag_generation():
    """Test the updated tag generation with sample tasks."""
    
    # Load existing tasks for comparison
    with open('catalyst_league_tasks.json', 'r') as f:
        data = json.load(f)
    
    # Create scraper instance
    scraper = CatalystLeagueScraper()
    
    print("TESTING TAG GENERATION")
    print("=" * 60)
    
    # Test with first 10 tasks
    for i, task in enumerate(data['tasks'][:10]):
        original_tags = task.get('Tags', [])
        
        # Generate new tags using updated logic
        new_tags = scraper.generate_tags(
            task['Task'],
            task['Information'],
            task['Requirements'],
            task['Area'],
            task['Pts']
        )
        
        print(f"\n{i+1}. {task['Task'][:50]}...")
        print(f"   Area: {task['Area']}, Pts: {task['Pts']}")
        print(f"   Original tags: {original_tags}")
        print(f"   New tags:      {new_tags}")
        
        # Check if new tags match original
        original_set = set(original_tags)
        new_set = set(new_tags)
        
        if original_set == new_set:
            print("   ✅ PERFECT MATCH")
        else:
            missing = original_set - new_set
            extra = new_set - original_set
            if missing:
                print(f"   ❌ Missing: {list(missing)}")
            if extra:
                print(f"   ➕ Extra: {list(extra)}")

def test_specific_cases():
    """Test specific edge cases."""
    scraper = CatalystLeagueScraper()
    
    print("\n\nTESTING SPECIFIC CASES")
    print("=" * 60)
    
    test_cases = [
        {
            'task': 'Progress through the Leagues tutorial to unlock your first relic.',
            'info': 'Progress through the Leagues tutorial to unlock your first relic .',
            'reqs': '',
            'area': 'Lumbridge',
            'pts': '10',
            'expected': ['Easy', '!Starting']
        },
        {
            'task': 'Kill the Giant Mole.',
            'info': 'Kill the Giant Mole.',
            'reqs': '',
            'area': 'Falador',
            'pts': '30',
            'expected': ['Medium', 'Killing']
        },
        {
            'task': 'Complete the Easy Falador Diary.',
            'info': 'Easy Falador diary',
            'reqs': 'See Easy Falador achievements page',
            'area': 'Falador',
            'pts': '30',
            'expected': ['Diary', 'Medium']
        }
    ]
    
    for i, case in enumerate(test_cases):
        tags = scraper.generate_tags(
            case['task'],
            case['info'],
            case['reqs'],
            case['area'],
            case['pts']
        )
        
        print(f"\n{i+1}. {case['task']}")
        print(f"   Expected: {case['expected']}")
        print(f"   Generated: {tags}")
        
        if set(tags) == set(case['expected']):
            print("   ✅ MATCH")
        else:
            print("   ❌ NO MATCH")

if __name__ == "__main__":
    test_tag_generation()
    test_specific_cases()
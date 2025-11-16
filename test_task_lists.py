#!/usr/bin/env python3
"""Test task list parsing in markdown_to_tiptap converter."""

import json
from markdown_to_tiptap import MarkdownToTiptapConverter

def test_simple_task_list():
    """Test basic task list parsing."""
    converter = MarkdownToTiptapConverter()
    
    markdown = """Here's a task list:

- [ ] First unchecked item
- [x] Second checked item
- [ ] Third unchecked item

And some text after."""
    
    result = converter.parse_markdown(markdown)
    
    print("Test 1: Simple Task List")
    print("=" * 50)
    print("Input Markdown:")
    print(markdown)
    print("\nOutput JSON:")
    print(json.dumps(result, indent=2))
    print("\n")
    
    # Verify structure
    assert any(node.get('type') == 'taskList' for node in result), "Should contain taskList node"
    
    task_list = next(node for node in result if node.get('type') == 'taskList')
    assert len(task_list['content']) == 3, "Should have 3 task items"
    
    # Check first item
    assert task_list['content'][0]['attrs']['checked'] == False
    assert task_list['content'][0]['content'][0]['content'][0]['text'] == "First unchecked item"
    
    # Check second item
    assert task_list['content'][1]['attrs']['checked'] == True
    assert task_list['content'][1]['content'][0]['content'][0]['text'] == "Second checked item"
    
    print("✅ Test 1 passed!")

def test_mixed_content():
    """Test task list mixed with other content."""
    converter = MarkdownToTiptapConverter()
    
    markdown = """# Project Tasks

Here are the things to do:

- [ ] Design the interface
- [x] Implement backend API
- [ ] Write documentation

## Notes

Regular bullet list:
- Item one
- Item two"""
    
    result = converter.parse_markdown(markdown)
    
    print("Test 2: Mixed Content")
    print("=" * 50)
    print("Input Markdown:")
    print(markdown)
    print("\nOutput JSON:")
    print(json.dumps(result, indent=2))
    print("\n")
    
    # Should have: heading, paragraph, taskList, heading, paragraph, bulletList
    assert result[0]['type'] == 'heading'
    assert any(node.get('type') == 'taskList' for node in result), "Should contain taskList"
    assert any(node.get('type') == 'bulletList' for node in result), "Should contain bulletList"
    
    print("✅ Test 2 passed!")

def test_uppercase_x():
    """Test uppercase X in checkbox."""
    converter = MarkdownToTiptapConverter()
    
    markdown = """- [X] Uppercase X should work
- [x] Lowercase x should work
- [ ] Unchecked should work"""
    
    result = converter.parse_markdown(markdown)
    
    print("Test 3: Uppercase X")
    print("=" * 50)
    print("Input Markdown:")
    print(markdown)
    print("\nOutput JSON:")
    print(json.dumps(result, indent=2))
    print("\n")
    
    task_list = result[0]
    assert task_list['content'][0]['attrs']['checked'] == True, "Uppercase X should be checked"
    assert task_list['content'][1]['attrs']['checked'] == True, "Lowercase x should be checked"
    assert task_list['content'][2]['attrs']['checked'] == False, "Empty should be unchecked"
    
    print("✅ Test 3 passed!")

def test_inline_formatting():
    """Test task items with inline formatting."""
    converter = MarkdownToTiptapConverter()
    
    markdown = """- [ ] Read **important** document
- [x] Write *code* for the feature
- [ ] Test the `implementation`"""
    
    result = converter.parse_markdown(markdown)
    
    print("Test 4: Inline Formatting")
    print("=" * 50)
    print("Input Markdown:")
    print(markdown)
    print("\nOutput JSON:")
    print(json.dumps(result, indent=2))
    print("\n")
    
    task_list = result[0]
    
    # First item should have bold
    first_item_content = task_list['content'][0]['content'][0]['content']
    assert any('bold' in str(mark.get('marks', [])) for mark in first_item_content if mark.get('marks'))
    
    print("✅ Test 4 passed!")

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("TASK LIST PARSING TESTS")
    print("=" * 50 + "\n")
    
    try:
        test_simple_task_list()
        test_mixed_content()
        test_uppercase_x()
        test_inline_formatting()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

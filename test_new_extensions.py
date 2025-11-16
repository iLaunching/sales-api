#!/usr/bin/env python3
"""Test new extensions: blockquote, horizontal rule, image, mathematics, mentions."""

import json
from markdown_to_tiptap import MarkdownToTiptapConverter

def test_blockquote():
    """Test blockquote parsing."""
    converter = MarkdownToTiptapConverter()
    
    markdown = """Regular paragraph.

> This is a blockquote
> spanning multiple lines
> with great content

Another paragraph."""
    
    result = converter.parse_markdown(markdown)
    
    print("Test 1: Blockquote")
    print("=" * 50)
    print("Input Markdown:")
    print(markdown)
    print("\nOutput JSON:")
    print(json.dumps(result, indent=2))
    print("\n")
    
    # Verify structure
    assert any(node.get('type') == 'blockquote' for node in result), "Should contain blockquote node"
    blockquote = next(node for node in result if node.get('type') == 'blockquote')
    assert blockquote['content'][0]['type'] == 'paragraph'
    
    print("✅ Test 1 passed!")

def test_horizontal_rule():
    """Test horizontal rule parsing."""
    converter = MarkdownToTiptapConverter()
    
    markdown = """Section one

---

Section two

***

Section three

___

Final section"""
    
    result = converter.parse_markdown(markdown)
    
    print("Test 2: Horizontal Rule")
    print("=" * 50)
    print("Input Markdown:")
    print(markdown)
    print("\nOutput JSON:")
    print(json.dumps(result, indent=2))
    print("\n")
    
    # Should have 3 horizontal rules
    hr_count = sum(1 for node in result if node.get('type') == 'horizontalRule')
    assert hr_count == 3, f"Should have 3 horizontal rules, got {hr_count}"
    
    print("✅ Test 2 passed!")

def test_images():
    """Test image parsing."""
    converter = MarkdownToTiptapConverter()
    
    markdown = """Here's an image:

![Alt text](https://example.com/image.jpg)

And another ![icon](https://example.com/icon.png) inline."""
    
    result = converter.parse_markdown(markdown)
    
    print("Test 3: Images")
    print("=" * 50)
    print("Input Markdown:")
    print(markdown)
    print("\nOutput JSON:")
    print(json.dumps(result, indent=2))
    print("\n")
    
    # Verify structure
    assert any(node.get('type') == 'image' for node in result), "Should contain image node"
    image = next(node for node in result if node.get('type') == 'image')
    assert image['attrs']['src'] == 'https://example.com/image.jpg'
    assert image['attrs']['alt'] == 'Alt text'
    
    print("✅ Test 3 passed!")

def test_math_blocks():
    """Test mathematics block parsing."""
    converter = MarkdownToTiptapConverter()
    
    markdown = """The quadratic formula:

$$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$$

And more text."""
    
    result = converter.parse_markdown(markdown)
    
    print("Test 4: Mathematics")
    print("=" * 50)
    print("Input Markdown:")
    print(markdown)
    print("\nOutput JSON:")
    print(json.dumps(result, indent=2))
    print("\n")
    
    # Verify structure
    assert any(node.get('type') == 'mathematics' for node in result), "Should contain mathematics node"
    math = next(node for node in result if node.get('type') == 'mathematics')
    assert 'frac' in math['attrs']['latex']
    
    print("✅ Test 4 passed!")

def test_mixed_content():
    """Test all new features together."""
    converter = MarkdownToTiptapConverter()
    
    markdown = """# New Features Demo

Here's a paragraph.

> This is a blockquote with **bold** text

---

![Logo](https://example.com/logo.png)

$$E = mc^2$$

- [ ] Task one
- [x] Task two

Final paragraph."""
    
    result = converter.parse_markdown(markdown)
    
    print("Test 5: Mixed Content")
    print("=" * 50)
    print("Input Markdown:")
    print(markdown)
    print("\nOutput JSON:")
    print(json.dumps(result, indent=2))
    print("\n")
    
    # Verify all types present
    types = [node.get('type') for node in result]
    assert 'heading' in types, "Should have heading"
    assert 'blockquote' in types, "Should have blockquote"
    assert 'horizontalRule' in types, "Should have horizontal rule"
    assert 'image' in types, "Should have image"
    assert 'mathematics' in types, "Should have mathematics"
    assert 'taskList' in types, "Should have task list"
    
    print("✅ Test 5 passed!")

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("NEW EXTENSIONS PARSING TESTS")
    print("=" * 50 + "\n")
    
    try:
        test_blockquote()
        test_horizontal_rule()
        test_images()
        test_math_blocks()
        test_mixed_content()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

"""
Example usage of the HTML Parser module for AI political analysis.
"""

from .parser import HTMLParser
from .exceptions import HTMLParsingError

# Example political HTML content
SAMPLE_POLITICAL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Political Analysis Report</title>
    <style>body { font-family: Arial; }</style>
    <script>console.log('tracking');</script>
</head>
<body>
    <nav class="navigation">
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/politics">Politics</a></li>
            <li><a href="/analysis">Analysis</a></li>
        </ul>
    </nav>
    
    <main>
        <article>
            <h1>Economic Policy Impact Analysis</h1>
            
            <h2>Executive Summary</h2>
            <p>The recent economic policy changes have significant implications 
               for political discourse and public opinion formation.</p>
            
            <h2>Key Findings</h2>
            <ul>
                <li>Policy approval rating increased by 15%</li>
                <li>Opposition sentiment decreased in urban areas</li>
                <li>Rural support remains unchanged</li>
            </ul>
            
            <h2>Statistical Analysis</h2>
            <table class="data-table">
                <tr>
                    <th>Region</th>
                    <th>Support %</th>
                    <th>Opposition %</th>
                    <th>Undecided %</th>
                </tr>
                <tr>
                    <td>Urban</td>
                    <td>65</td>
                    <td>25</td>
                    <td>10</td>
                </tr>
                <tr>
                    <td>Rural</td>
                    <td>45</td>
                    <td>40</td>
                    <td>15</td>
                </tr>
            </table>
            
            <blockquote>
                "The policy represents a significant shift in economic thinking," 
                stated the lead economist.
            </blockquote>
            
            <h2>Implications</h2>
            <p>These findings suggest a complex political landscape where 
               traditional voting patterns may be shifting.</p>
        </article>
    </main>
    
    <aside class="sidebar">
        <div class="advertisement">
            <h3>Related Content</h3>
            <button onclick="share()">Share Article</button>
        </div>
    </aside>
    
    <footer>
        <p>&copy; 2024 Political Analysis Center</p>
    </footer>
</body>
</html>
"""


def demonstrate_basic_parsing():
    """Demonstrate basic HTML parsing for AI analysis."""
    print("=== Basic HTML Parsing for AI Analysis ===\n")
    
    parser = HTMLParser()
    
    try:
        # Parse HTML content
        structured_content = parser.parse(SAMPLE_POLITICAL_HTML)
        
        print("AI-Optimized Content:")
        print("-" * 50)
        print(structured_content)
        print("\n" + "="*70 + "\n")
        
        # Extract metadata
        metadata = parser.get_metadata(SAMPLE_POLITICAL_HTML)
        
        print("Content Metadata:")
        print("-" * 50)
        for key, value in metadata.items():
            print(f"{key}: {value}")
        print("\n" + "="*70 + "\n")
        
    except HTMLParsingError as e:
        print(f"Parsing failed: {e}")


def demonstrate_error_handling():
    """Demonstrate error handling capabilities."""
    print("=== Error Handling Demonstration ===\n")
    
    parser = HTMLParser()
    
    # Test with empty content
    try:
        parser.parse("")
    except HTMLParsingError as e:
        print(f"Empty content error: {e}")
    
    # Test with invalid HTML
    try:
        parser.parse("<html><body><div>Unclosed div</body></html>")
        print("Invalid HTML was handled gracefully")
    except HTMLParsingError as e:
        print(f"Invalid HTML error: {e}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    demonstrate_basic_parsing()
    demonstrate_error_handling()
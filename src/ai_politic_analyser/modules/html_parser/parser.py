"""
Main HTML Parser implementation optimized for AI text analysis.
"""

import logging
from typing import Optional, List, Dict, Any
from bs4 import BeautifulSoup, Tag, NavigableString
from bs4.element import Comment

from .exceptions import HTMLParsingError, InvalidHTMLError, EmptyContentError

logger = logging.getLogger(__name__)


class HTMLParser:
    """
    HTML Parser optimized for AI political analysis.
    
    Extracts semantic content while preserving structure and adding
    contextual labels for better AI understanding.
    """
    
    def __init__(self, preserve_structure: bool = True):
        """
        Initialize the HTML parser.
        
        Args:
            preserve_structure: Whether to preserve structural elements like headings
        """
        self.preserve_structure = preserve_structure
        self._setup_removal_rules()
    
    def _setup_removal_rules(self) -> None:
        """Setup rules for element removal and processing."""
        # Elements to completely remove
        self.remove_elements = {
            'script', 'style', 'noscript', 'meta', 'link', 'title',
            'head', 'nav', 'footer', 'aside', 'form', 'input', 
            'button', 'select', 'textarea', 'iframe', 'object', 'embed'
        }
        
        # CSS classes that indicate technical/navigation content
        self.technical_classes = {
            'nav', 'navigation', 'menu', 'sidebar', 'footer', 'header',
            'advertisement', 'ad', 'social', 'share', 'breadcrumb',
            'pagination', 'toolbar', 'controls', 'widget'
        }
        
        # Table indicators for content vs technical classification
        self.content_table_indicators = {
            'data', 'results', 'statistics', 'stats', 'comparison',
            'schedule', 'timeline', 'budget', 'financial', 'economic'
        }
        
        self.technical_table_indicators = {
            'nav', 'menu', 'layout', 'grid', 'controls', 'buttons'
        }
    
    def parse(self, html_content: str) -> str:
        """
        Parse HTML content and return AI-optimized text.
        
        Args:
            html_content: Raw HTML string
            
        Returns:
            Structured text optimized for AI analysis
            
        Raises:
            HTMLParsingError: If parsing fails
            EmptyContentError: If no meaningful content found
        """
        if not html_content or not html_content.strip():
            raise EmptyContentError("HTML content is empty")
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Remove unwanted elements
            self._remove_technical_elements(soup)
            
            # Extract structured content
            structured_content = self._extract_structured_content(soup)
            
            if not structured_content.strip():
                raise EmptyContentError("No meaningful content found after parsing")
            
            return structured_content
            
        except Exception as e:
            logger.error(f"HTML parsing failed: {str(e)}")
            raise HTMLParsingError(f"Failed to parse HTML: {str(e)}") from e
    
    def _remove_technical_elements(self, soup: BeautifulSoup) -> None:
        """Remove technical and navigation elements."""
        # Remove by tag name
        for tag_name in self.remove_elements:
            for element in soup.find_all(tag_name):
                element.decompose()
        
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Remove by technical classes
        for class_name in self.technical_classes:
            for element in soup.find_all(class_=lambda x: x and any(class_name in cls.lower() for cls in x)):
                element.decompose()
    
    def _extract_structured_content(self, soup: BeautifulSoup) -> str:
        """Extract content with structural context labels."""
        content_parts = []
        
        # Process body or main content area
        body = soup.find('body') or soup
        main_content = body.find('main') or body.find('article') or body
        
        for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'table', 'blockquote']):
            if self._is_meaningful_element(element):
                processed_content = self._process_element(element)
                if processed_content:
                    content_parts.append(processed_content)
        
        return '\n\n'.join(content_parts)
    
    def _is_meaningful_element(self, element: Tag) -> bool:
        """Check if element contains meaningful content."""
        if not isinstance(element, Tag):
            return False
        
        # Check if element has been removed or is empty
        if not element.get_text(strip=True):
            return False
        
        # Check for technical classes
        element_classes = element.get('class', [])
        if any(tech_class in ' '.join(element_classes).lower() for tech_class in self.technical_classes):
            return False
        
        # Minimum content length threshold
        text_content = element.get_text(strip=True)
        return len(text_content) > 10
    
    def _process_element(self, element: Tag) -> Optional[str]:
        """Process individual elements with contextual labels."""
        tag_name = element.name.lower()
        
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return self._process_heading(element)
        elif tag_name == 'p':
            return self._process_paragraph(element)
        elif tag_name in ['ul', 'ol']:
            return self._process_list(element)
        elif tag_name == 'table':
            return self._process_table(element)
        elif tag_name == 'blockquote':
            return self._process_quote(element)
        
        return None
    
    def _process_heading(self, element: Tag) -> str:
        """Process heading elements with section labels."""
        level = element.name[1]  # Extract number from h1, h2, etc.
        text = element.get_text(strip=True)
        return f"Section (Level {level}): {text}"
    
    def _process_paragraph(self, element: Tag) -> str:
        """Process paragraph elements."""
        text = element.get_text(strip=True)
        return text
    
    def _process_list(self, element: Tag) -> str:
        """Process list elements with proper formatting."""
        list_type = "numbered" if element.name == 'ol' else "bulleted"
        items = []
        
        for i, li in enumerate(element.find_all('li', recursive=False), 1):
            item_text = li.get_text(strip=True)
            if item_text:
                if list_type == "numbered":
                    items.append(f"{i}. {item_text}")
                else:
                    items.append(f"• {item_text}")
        
        if items:
            return f"List ({list_type}):\n" + '\n'.join(items)
        return ""
    
    def _process_table(self, element: Tag) -> str:
        """Process table elements with content classification."""
        # Determine if this is a content table or technical table
        table_type = self._classify_table(element)
        
        if table_type == "technical":
            return ""  # Skip technical tables
        
        # Extract table title/caption
        table_title = "Data"
        caption = element.find('caption')
        if caption:
            table_title = caption.get_text(strip=True)
        else:
            # Try to find title from surrounding elements or table attributes
            title_attr = element.get('title', '') or element.get('data-title', '')
            if title_attr:
                table_title = title_attr
        
        # Extract table rows
        all_rows = element.find_all('tr')
        if not all_rows:
            return ""
        
        header_row = None
        data_rows = []
        
        # Check if first row is header (contains th elements or is in thead)
        first_row = all_rows[0]
        if first_row.find_all('th') or first_row.find_parent('thead'):
            header_row = first_row
            data_rows = all_rows[1:]
        else:
            data_rows = all_rows
        
        # Extract column names
        column_names = []
        if header_row:
            for cell in header_row.find_all(['th', 'td']):
                cell_text = cell.get_text(strip=True)
                if cell_text:
                    column_names.append(cell_text)
        
        # If no header found, create generic column names
        if not column_names and data_rows:
            first_data_row = data_rows[0]
            num_columns = len(first_data_row.find_all(['td', 'th']))
            column_names = [f"Column{i+1}" for i in range(num_columns)]
        
        if not column_names:
            return ""
        
        # Process data rows
        formatted_rows = []
        for row in data_rows:
            cells = []
            for cell in row.find_all(['td', 'th']):
                cell_text = cell.get_text(strip=True)
                cells.append(cell_text if cell_text else "")
            
            if cells:
                # Create column_name: value pairs
                row_parts = []
                for i, cell_value in enumerate(cells):
                    if i < len(column_names):
                        row_parts.append(f"{column_names[i]}: {cell_value}")
                
                if row_parts:
                    formatted_rows.append(" | ".join(row_parts))
        
        if formatted_rows:
            result = f"Table: {table_title}\n" + '\n'.join(formatted_rows)
            return result
        
        return ""
    
    def _process_quote(self, element: Tag) -> str:
        """Process blockquote elements."""
        text = element.get_text(strip=True)
        return f"Quote: {text}"
    
    def _classify_table(self, table: Tag) -> str:
        """Classify table as content or technical."""
        # Check class names
        table_classes = ' '.join(table.get('class', [])).lower()
        
        if any(indicator in table_classes for indicator in self.content_table_indicators):
            return "content"
        
        if any(indicator in table_classes for indicator in self.technical_table_indicators):
            return "technical"
        
        # Check content characteristics
        text_content = table.get_text().lower()
        
        # Look for data patterns (numbers, dates, etc.)
        import re
        number_pattern = r'\d+[.,]?\d*[%$]?'
        numbers_count = len(re.findall(number_pattern, text_content))
        
        # If table has many numbers or data indicators, likely content
        if numbers_count > 5 or any(indicator in text_content for indicator in self.content_table_indicators):
            return "content"
        
        # Check for navigation indicators
        if any(indicator in text_content for indicator in ['home', 'about', 'contact', 'menu', 'navigation']):
            return "technical"
        
        # Default to content for political analysis
        return "content"
    
    def get_metadata(self, html_content: str) -> Dict[str, Any]:
        """
        Extract metadata from HTML for analysis context.
        
        Args:
            html_content: Raw HTML string
            
        Returns:
            Dictionary containing metadata
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            metadata = {
                'title': self._extract_title(soup),
                'headings_count': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                'paragraphs_count': len(soup.find_all('p')),
                'lists_count': len(soup.find_all(['ul', 'ol'])),
                'tables_count': len(soup.find_all('table')),
                'links_count': len(soup.find_all('a'))
            }
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {str(e)}")
            return {}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        # Fallback to h1
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text(strip=True)
        
        return "No title found"
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
        
        # CSS classes that indicate technical/navigation content (exact matches only)
        self.technical_classes = {
            'nav', 'navigation', 'menu', 'sidebar', 'footer', 'header',
            'advertisement', 'ad'
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
        
        # Remove by technical classes (exact matches only)
        for class_name in self.technical_classes:
            for element in soup.find_all(class_=lambda x: x and class_name in x):
                element.decompose()
    
    def _extract_structured_content(self, soup: BeautifulSoup) -> str:
        """Extract content with structural context labels using blacklist approach."""
        content_parts = []
        
        # Process body or main content area
        body = soup.find('body') or soup
        main_content = body.find('main') or body.find('article') or body
        
        # Process elements recursively, prioritizing top-level block elements
        self._extract_content_recursive(main_content, content_parts, set())
        
        return '\n\n'.join(content_parts)
    
    def _extract_content_recursive(self, element: Tag, content_parts: list, processed_elements: set):
        """Recursively extract content while preserving structure."""
        if not isinstance(element, Tag) or id(element) in processed_elements:
            return
        
        if self._is_technical_element(element):
            return
        
        # Mark as processed to avoid duplicates
        processed_elements.add(id(element))
        
        tag_name = element.name.lower() if element.name else ""
        
        # Handle specific structural elements with special formatting
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            content = self._process_heading(element)
            if content:
                content_parts.append(content)
            return
        elif tag_name in ['ul', 'ol']:
            content = self._process_list(element)
            if content:
                content_parts.append(content)
            return
        elif tag_name == 'table':
            content = self._process_table(element)
            if content:
                content_parts.append(content)
            return
        elif tag_name == 'blockquote':
            content = self._process_quote(element)
            if content:
                content_parts.append(content)
            return
        elif tag_name == 'p':
            content = self._process_paragraph(element)
            if content:
                content_parts.append(content)
            return
        
        # For other elements, check if they contain meaningful direct text
        direct_text = ""
        has_block_children = False
        
        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    direct_text += text + " "
            elif isinstance(child, Tag):
                child_tag = child.name.lower()
                # Check if child is a block-level element
                if child_tag in ['div', 'p', 'section', 'article', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'table', 'blockquote']:
                    has_block_children = True
                    # Process child recursively
                    self._extract_content_recursive(child, content_parts, processed_elements)
        
        # If element has direct meaningful text and no block children, add it as content
        if direct_text.strip() and len(direct_text.strip()) >= 10 and not has_block_children:
            content_parts.append(direct_text.strip())
        elif not has_block_children:
            # If no block children, extract all text content as a block
            text_content = element.get_text(strip=True)
            if text_content and len(text_content) >= 10:
                content_parts.append(text_content)
    
    def _has_processed_parent(self, element: Tag, processed_elements: set) -> bool:
        """Check if any parent of this element has already been processed."""
        parent = element.parent
        while parent and hasattr(parent, 'name'):
            if id(parent) in processed_elements:
                return True
            parent = parent.parent
        return False
    
    def _is_technical_element(self, element: Tag) -> bool:
        """Check if element is a technical/non-content element that should be excluded."""
        if not isinstance(element, Tag):
            return False
        
        tag_name = element.name.lower()
        
        # Check if it's a technical tag (these were already removed, but double-check)
        if tag_name in self.remove_elements:
            return True
        
        # Check for technical classes (exact matches only)
        element_classes = element.get('class', [])
        if any(tech_class in element_classes for tech_class in self.technical_classes):
            return True
        
        return False
    
    def _is_meaningful_element(self, element: Tag) -> bool:
        """Check if element contains meaningful content."""
        if not isinstance(element, Tag):
            return False
        
        # Check if element has meaningful text content
        text_content = element.get_text(strip=True)
        if not text_content or len(text_content) < 10:
            return False
        
        # Check if element has any child elements that we might want to process
        # Skip if all children are already processed (avoid duplicate processing)
        return True
    
    def _process_element(self, element: Tag) -> Optional[str]:
        """Process individual elements with contextual labels."""
        tag_name = element.name.lower()
        
        # Process specific structural elements with special formatting
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return self._process_heading(element)
        elif tag_name in ['ul', 'ol']:
            return self._process_list(element)
        elif tag_name == 'table':
            return self._process_table(element)
        elif tag_name == 'blockquote':
            return self._process_quote(element)
        elif tag_name == 'p':
            return self._process_paragraph(element)
        else:
            # For all other block-level elements, process them with structure preservation
            return self._process_generic_block(element)
        
        return None
    
    def _process_generic_block(self, element: Tag) -> Optional[str]:
        """Process generic block elements while preserving internal structure."""
        tag_name = element.name.lower()
        
        # Define block-level elements that should have their content processed with structure
        block_elements = {
            'div', 'section', 'article', 'main', 'header', 'aside', 'span',
            'figure', 'figcaption', 'details', 'summary'
        }
        
        if tag_name in block_elements:
            # For block elements, process child text nodes and elements separately
            content_parts = []
            
            # Get direct text content and child elements
            for child in element.children:
                if isinstance(child, NavigableString):
                    # Direct text content
                    text = str(child).strip()
                    if text and len(text) >= 10:
                        content_parts.append(text)
                elif isinstance(child, Tag):
                    # Child elements - check if they contain meaningful content
                    child_text = child.get_text(strip=True)
                    if child_text and len(child_text) >= 10:
                        # For nested elements, extract structured content
                        if child.name.lower() in ['p', 'div', 'span', 'section']:
                            content_parts.append(child_text)
            
            if content_parts:
                return '\n\n'.join(content_parts)
        else:
            # For inline or other elements, just extract text
            text = element.get_text(strip=True)
            if text and len(text) >= 10:
                return text
        
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
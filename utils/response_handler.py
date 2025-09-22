import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import markdown
from urllib.parse import urlparse

class ResponseHandler:
    """Handles processing and formatting of AI responses"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.markdown_processor = markdown.Markdown(
            extensions=['codehilite', 'fenced_code', 'tables', 'toc']
        )
    
    def process_response(self, raw_response: str, context: Dict = None) -> Dict[str, Any]:
        """
        Process raw AI response and return formatted data
        
        Args:
            raw_response: Raw response from AI model
            context: Optional context dictionary
            
        Returns:
            Dictionary with processed response data
        """
        try:
            # Clean the response
            cleaned_response = self._clean_response(raw_response)
            
            # Extract metadata
            metadata = self._extract_metadata(cleaned_response)
            
            # Format for different outputs
            formatted_response = {
                "original": raw_response,
                "cleaned": cleaned_response,
                "html": self._convert_to_html(cleaned_response),
                "plain_text": self._convert_to_plain_text(cleaned_response),
                "metadata": metadata,
                "word_count": len(cleaned_response.split()),
                "character_count": len(cleaned_response),
                "processing_time": datetime.now().isoformat(),
                "has_code": self._has_code_blocks(cleaned_response),
                "has_links": self._has_links(cleaned_response),
                "has_lists": self._has_lists(cleaned_response),
                "sentiment": self._analyze_sentiment(cleaned_response),
                "language": self._detect_language(cleaned_response),
                "action_items": self.extract_action_items(cleaned_response),
                "key_points": self.extract_key_points(cleaned_response)
            }
            
            return formatted_response
            
        except Exception as e:
            self.logger.error(f"Error processing response: {e}")
            return {
                "original": raw_response,
                "cleaned": raw_response,
                "html": raw_response,
                "plain_text": raw_response,
                "metadata": {},
                "error": str(e)
            }
    
    def _clean_response(self, response: str) -> str:
        """
        Clean and normalize the response text
        
        Args:
            response: Raw response text
            
        Returns:
            Cleaned response text
        """
        # Remove thinking tags and content
        response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
        response = re.sub(r"<thinking>.*?</thinking>", "", response, flags=re.DOTALL)
        
        # Remove excessive whitespace
        response = re.sub(r'\n\s*\n\s*\n', '\n\n', response)
        response = re.sub(r' +', ' ', response)
        
        # Fix common formatting issues
        response = re.sub(r'([.!?])\s*\n\s*([A-Z])', r'\1 \2', response)
        
        # Clean up code blocks
        response = re.sub(r'```(\w+)?\n', r'```\1\n', response)
        
        # Remove trailing whitespace from lines
        response = '\n'.join(line.rstrip() for line in response.split('\n'))
        
        return response.strip()
    
    def _extract_metadata(self, response: str) -> Dict[str, Any]:
        """
        Extract metadata from the response
        
        Args:
            response: Cleaned response text
            
        Returns:
            Dictionary with extracted metadata
        """
        metadata = {}
        
        # Extract code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', response, re.DOTALL)
        if code_blocks:
            metadata['code_blocks'] = [
                {
                    'language': block[0] if block[0] else 'text',
                    'code': block[1].strip()
                }
                for block in code_blocks
            ]
        
        # Extract links
        links = re.findall(r'https?://[^\s\)]+', response)
        if links:
            metadata['links'] = links
        
        # Extract markdown links
        md_links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', response)
        if md_links:
            metadata['markdown_links'] = [
                {'text': link[0], 'url': link[1]}
                for link in md_links
            ]
        
        # Extract headers
        headers = re.findall(r'^#+\s+(.+)$', response, re.MULTILINE)
        if headers:
            metadata['headers'] = headers
        
        # Extract lists
        lists = re.findall(r'^[\*\-\+]\s+(.+)$', response, re.MULTILINE)
        if lists:
            metadata['list_items'] = lists
        
        # Extract numbered lists
        numbered_lists = re.findall(r'^\d+\.\s+(.+)$', response, re.MULTILINE)
        if numbered_lists:
            metadata['numbered_list_items'] = numbered_lists
        
        # Extract mentions/tags
        mentions = re.findall(r'@\w+', response)
        if mentions:
            metadata['mentions'] = mentions
        
        # Extract hashtags
        hashtags = re.findall(r'#\w+', response)
        if hashtags:
            metadata['hashtags'] = hashtags
        
        return metadata
    
    def _convert_to_html(self, response: str) -> str:
        """
        Convert response to HTML format
        
        Args:
            response: Cleaned response text
            
        Returns:
            HTML formatted response
        """
        try:
            # Convert markdown to HTML
            html = self.markdown_processor.convert(response)
            
            # Add custom styling classes
            html = re.sub(r'<h([1-6])', r'<h\1 class="response-header"', html)
            html = re.sub(r'<p>', r'<p class="response-paragraph">', html)
            html = re.sub(r'<code>', r'<code class="response-code">', html)
            html = re.sub(r'<pre>', r'<pre class="response-pre">', html)
            html = re.sub(r'<blockquote>', r'<blockquote class="response-quote">', html)
            html = re.sub(r'<ul>', r'<ul class="response-list">', html)
            html = re.sub(r'<ol>', r'<ol class="response-list">', html)
            html = re.sub(r'<table>', r'<table class="response-table">', html)
            
            # Make links open in new tab
            html = re.sub(r'<a href="([^"]+)">', r'<a href="\1" target="_blank" rel="noopener noreferrer">', html)
            
            return html
            
        except Exception as e:
            self.logger.error(f"Error converting to HTML: {e}")
            return f'<p>{response}</p>'
    
    def _convert_to_plain_text(self, response: str) -> str:
        """
        Convert response to plain text (remove markdown)
        
        Args:
            response: Cleaned response text
            
        Returns:
            Plain text response
        """
        # Remove markdown formatting
        text = re.sub(r'[*_`~]', '', response)
        text = re.sub(r'#+\s+', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        text = re.sub(r'>\s+', '', text)
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Clean up excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def _has_code_blocks(self, response: str) -> bool:
        """Check if response contains code blocks"""
        return bool(re.search(r'```', response))
    
    def _has_links(self, response: str) -> bool:
        """Check if response contains links"""
        return bool(re.search(r'https?://[^\s\)]+', response))
    
    def _has_lists(self, response: str) -> bool:
        """Check if response contains lists"""
        return bool(re.search(r'^[\*\-\+\d+\.]\s+', response, re.MULTILINE))
    
    def _analyze_sentiment(self, response: str) -> str:
        """
        Simple sentiment analysis
        
        Args:
            response: Response text
            
        Returns:
            Sentiment classification (positive, negative, neutral)
        """
        # Simple keyword-based sentiment analysis
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'perfect', 'brilliant', 'outstanding', 'superb', 'helpful', 'useful',
            'love', 'like', 'enjoy', 'pleased', 'happy', 'glad', 'excited',
            'awesome', 'incredible', 'impressive', 'remarkable', 'fabulous'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'dislike',
            'wrong', 'error', 'problem', 'issue', 'difficult', 'hard', 'impossible',
            'failed', 'failure', 'broken', 'sorry', 'unfortunately', 'sad',
            'disappointed', 'frustrated', 'annoyed', 'angry', 'upset'
        ]
        
        words = response.lower().split()
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _detect_language(self, response: str) -> str:
        """
        Simple language detection
        
        Args:
            response: Response text
            
        Returns:
            Detected language code
        """
        # Simple heuristic - check for common patterns
        # This is a basic implementation, for production use a proper language detection library
        
        # Check for common English words
        english_indicators = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        words = response.lower().split()
        
        english_count = sum(1 for word in words if word in english_indicators)
        
        if len(words) > 0 and english_count / len(words) > 0.1:
            return 'en'
        
        return 'unknown'
    
    def format_for_display(self, response: str, display_type: str = 'html') -> str:
        """
        Format response for specific display type
        
        Args:
            response: Raw response text
            display_type: Type of display (html, markdown, plain, streamlit)
            
        Returns:
            Formatted response
        """
        processed = self.process_response(response)
        
        if display_type == 'html':
            return processed['html']
        elif display_type == 'markdown':
            return processed['cleaned']
        elif display_type == 'plain':
            return processed['plain_text']
        elif display_type == 'streamlit':
            return self._format_for_streamlit(processed['cleaned'])
        else:
            return processed['cleaned']
    
    def _format_for_streamlit(self, response: str) -> str:
        """
        Format response specifically for Streamlit display
        
        Args:
            response: Cleaned response text
            
        Returns:
            Streamlit-formatted response
        """
        # Streamlit handles markdown natively, so we just need to ensure
        # proper formatting for code blocks and other elements
        
        # Ensure code blocks are properly formatted
        response = re.sub(r'```(\w+)?\n', r'```\1\n', response)
        
        # Ensure proper spacing around headers
        response = re.sub(r'\n(#+\s+)', r'\n\n\1', response)
        
        # Ensure proper spacing around lists
        response = re.sub(r'\n([\*\-\+]\s+)', r'\n\n\1', response)
        response = re.sub(r'\n(\d+\.\s+)', r'\n\n\1', response)
        
        return response
    
    def extract_action_items(self, response: str) -> List[str]:
        """
        Extract action items from response
        
        Args:
            response: Response text
            
        Returns:
            List of action items
        """
        action_items = []
        
        # Look for action-oriented phrases
        action_patterns = [
            r'(?i)you should (.+)',
            r'(?i)you need to (.+)',
            r'(?i)you must (.+)',
            r'(?i)you can (.+)',
            r'(?i)try to (.+)',
            r'(?i)consider (.+)',
            r'(?i)make sure to (.+)',
            r'(?i)don\'t forget to (.+)',
            r'(?i)remember to (.+)',
            r'(?i)it\'s important to (.+)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, response)
            action_items.extend(matches)
        
        # Look for numbered action items
        numbered_actions = re.findall(r'^\d+\.\s+(.+)$', response, re.MULTILINE)
        action_items.extend(numbered_actions)
        
        # Look for bulleted action items
        bulleted_actions = re.findall(r'^[\*\-\+]\s+(.+)$', response, re.MULTILINE)
        action_items.extend(bulleted_actions)
        
        # Clean and deduplicate
        cleaned_actions = []
        for item in action_items:
            cleaned = item.strip().rstrip('.')
            if cleaned and cleaned not in cleaned_actions:
                cleaned_actions.append(cleaned)
        
        return cleaned_actions[:10]  # Return top 10 action items
    
    def extract_key_points(self, response: str) -> List[str]:
        """
        Extract key points from response
        
        Args:
            response: Response text
            
        Returns:
            List of key points
        """
        key_points = []
        
        # Extract sentences with key indicators
        sentences = re.split(r'[.!?]+', response)
        
        key_indicators = [
            'important', 'key', 'main', 'primary', 'essential', 'crucial',
            'significant', 'notable', 'remember', 'note that', 'keep in mind',
            'in summary', 'to summarize', 'in conclusion', 'overall',
            'the point is', 'basically', 'fundamentally'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Ignore very short sentences
                for indicator in key_indicators:
                    if indicator in sentence.lower():
                        key_points.append(sentence)
                        break
        
        # Extract headers as key points
        headers = re.findall(r'^#+\s+(.+)$', response, re.MULTILINE)
        key_points.extend(headers)
        
        # Remove duplicates and limit
        unique_points = []
        for point in key_points:
            if point not in unique_points:
                unique_points.append(point)
        
        return unique_points[:8]  # Return top 8 key points
    
    def get_response_summary(self, response: str) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the response
        
        Args:
            response: Response text
            
        Returns:
            Dictionary with response summary
        """
        processed = self.process_response(response)
        
        return {
            'length': {
                'words': processed['word_count'],
                'characters': processed['character_count'],
                'lines': len(processed['cleaned'].split('\n'))
            },
            'content_types': {
                'has_code': processed['has_code'],
                'has_links': processed['has_links'],
                'has_lists': processed['has_lists'],
                'code_blocks': len(processed['metadata'].get('code_blocks', [])),
                'links': len(processed['metadata'].get('links', [])),
                'headers': len(processed['metadata'].get('headers', []))
            },
            'analysis': {
                'sentiment': processed['sentiment'],
                'language': processed['language'],
                'action_items_count': len(processed['action_items']),
                'key_points_count': len(processed['key_points'])
            },
            'action_items': processed['action_items'],
            'key_points': processed['key_points']
        }
    
    def validate_response(self, response: str) -> Dict[str, Any]:
        """
        Validate response quality and completeness
        
        Args:
            response: Response text
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'is_valid': True,
            'issues': [],
            'warnings': [],
            'quality_score': 0
        }
        
        # Check for minimum length
        if len(response.strip()) < 10:
            validation_results['is_valid'] = False
            validation_results['issues'].append('Response too short')
        
        # Check for unfinished code blocks
        if response.count('```') % 2 != 0:
            validation_results['is_valid'] = False
            validation_results['issues'].append('Unfinished code block')
        
        # Check for excessive repetition
        words = response.lower().split()
        if len(words) > 20:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            max_count = max(word_counts.values())
            if max_count > len(words) * 0.1:  # More than 10% repetition
                validation_results['warnings'].append('High word repetition detected')
        
        # Check for proper sentence structure
        sentences = re.split(r'[.!?]+', response)
        incomplete_sentences = [s for s in sentences if len(s.strip()) > 0 and len(s.strip()) < 3]
        if len(incomplete_sentences) > 2:
            validation_results['warnings'].append('Multiple incomplete sentences')
        
        # Calculate quality score
        quality_score = 100
        quality_score -= len(validation_results['issues']) * 20
        quality_score -= len(validation_results['warnings']) * 5
        
        # Bonus for good formatting
        if self._has_code_blocks(response):
            quality_score += 5
        if self._has_lists(response):
            quality_score += 5
        if len(re.findall(r'^#+\s+(.+)$', response, re.MULTILINE)) > 0:
            quality_score += 5
        
        validation_results['quality_score'] = max(0, min(100, quality_score))
        
        return validation_results


# Example usage and testing
if __name__ == "__main__":
    # Initialize the handler
    handler = ResponseHandler()
    
    # Test with a sample response
    sample_response = """
    # Sample AI Response
    
    This is a sample response that demonstrates the capabilities of the ResponseHandler class.
    
    ## Key Features
    
    - **Text Processing**: Cleans and normalizes AI responses
    - **Metadata Extraction**: Extracts links, code blocks, headers, etc.
    - **Format Conversion**: Converts to HTML, plain text, and more
    - **Content Analysis**: Analyzes sentiment, language, and structure
    
    ### Code Example
    
    ```python
    def hello_world():
        print("Hello, World!")
        return "success"
    ```
    
    You should try using this handler in your application. It's important to note that 
    this is a comprehensive solution for response processing.
    
    ## Action Items
    
    1. Install required dependencies
    2. Import the ResponseHandler class
    3. Process your AI responses
    
    For more information, visit https://example.com
    """
    
    # Process the response
    result = handler.process_response(sample_response)
    
    # Print results
    print("=== Response Processing Results ===")
    print(f"Word Count: {result['word_count']}")
    print(f"Character Count: {result['character_count']}")
    print(f"Has Code: {result['has_code']}")
    print(f"Has Links: {result['has_links']}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Language: {result['language']}")
    
    print("\n=== Action Items ===")
    for i, item in enumerate(result['action_items'], 1):
        print(f"{i}. {item}")
    
    print("\n=== Key Points ===")
    for i, point in enumerate(result['key_points'], 1):
        print(f"{i}. {point}")
    
    print("\n=== Validation Results ===")
    validation = handler.validate_response(sample_response)
    print(f"Quality Score: {validation['quality_score']}/100")
    print(f"Issues: {validation['issues']}")
    print(f"Warnings: {validation['warnings']}")
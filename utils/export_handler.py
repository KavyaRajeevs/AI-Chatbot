import json
import csv
import io
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple
import base64
import weasyprint

class ExportHandler:
    """Enhanced export handler for multiple formats"""
    
    def __init__(self):
        self.supported_formats = ['txt', 'json', 'csv', 'html', 'pdf']
    
    def export_chat(self, messages: List[Dict], format_type: str, conversation_id: str) -> Tuple[str, str]:
        """
        Export chat messages in various formats
        
        Args:
            messages: List of message dictionaries
            format_type: Export format (txt, json, csv, html, pdf)
            conversation_id: Unique conversation identifier
            
        Returns:
            Tuple of (file_data, mime_type)
        """
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}")
        
        export_methods = {
            'txt': self._export_txt,
            'json': self._export_json,
            'csv': self._export_csv,
            'html': self._export_html,
            'pdf': self._export_pdf
        }
        
        return export_methods[format_type](messages, conversation_id)
    
    def _export_txt(self, messages: List[Dict], conversation_id: str) -> Tuple[str, str]:
        """Export as plain text"""
        content = []
        content.append("=" * 60)
        content.append("AI CHATBOT CONVERSATION")
        content.append("=" * 60)
        content.append(f"Conversation ID: {conversation_id}")
        content.append(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"Total Messages: {len(messages)}")
        content.append("=" * 60)
        content.append("")
        
        for i, msg in enumerate(messages, 1):
            role = "USER" if msg["role"] == "user" else "ASSISTANT"
            timestamp = msg.get("timestamp", "N/A")
            content.append(f"[{i:03d}] {role} [{timestamp}]:")
            content.append(f"{msg['content']}")
            content.append("-" * 40)
            content.append("")
        
        content.append("=" * 60)
        content.append("End of Conversation")
        content.append("=" * 60)
        
        return "\n".join(content), "text/plain"
    
    def _export_json(self, messages: List[Dict], conversation_id: str) -> Tuple[str, str]:
        """Export as JSON"""
        export_data = {
            "conversation_id": conversation_id,
            "export_date": datetime.now().isoformat(),
            "total_messages": len(messages),
            "messages": messages,
            "metadata": {
                "user_messages": len([m for m in messages if m["role"] == "user"]),
                "assistant_messages": len([m for m in messages if m["role"] == "assistant"]),
                "conversation_duration": self._calculate_duration(messages),
                "export_version": "1.0"
            }
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False), "application/json"
    
    def _export_csv(self, messages: List[Dict], conversation_id: str) -> Tuple[str, str]:
        """Export as CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Message_ID",
            "Role",
            "Content",
            "Timestamp",
            "Word_Count",
            "Character_Count",
            "Conversation_ID"
        ])
        
        # Write messages
        for i, msg in enumerate(messages, 1):
            content = msg["content"]
            writer.writerow([
                msg.get("message_id", f"msg_{i}"),
                msg["role"],
                content,
                msg.get("timestamp", "N/A"),
                len(content.split()),
                len(content),
                conversation_id
            ])
        
        return output.getvalue(), "text/csv"
    
    def _export_html(self, messages: List[Dict], conversation_id: str) -> Tuple[str, str]:
        """Export as HTML"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Chatbot Conversation - {conversation_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .conversation {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .message {{
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 10px;
            position: relative;
        }}
        .user-message {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: 50px;
        }}
        .assistant-message {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            margin-right: 50px;
        }}
        .role {{
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        .timestamp {{
            font-size: 12px;
            opacity: 0.7;
            margin-top: 10px;
        }}
        .content {{
            line-height: 1.6;
            white-space: pre-wrap;
        }}
        .stats {{
            background: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI Chatbot Conversation</h1>
        <p>Conversation ID: {conversation_id}</p>
        <p>Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="conversation">
        <h2>Messages ({len(messages)} total)</h2>
"""
        
        for i, msg in enumerate(messages, 1):
            role_class = "user-message" if msg["role"] == "user" else "assistant-message"
            role_display = "👤 You" if msg["role"] == "user" else "🤖 Assistant"
            
            html_content += f"""
        <div class="message {role_class}">
            <div class="role">{role_display}</div>
            <div class="content">{self._escape_html(msg['content'])}</div>
            <div class="timestamp">{msg.get('timestamp', 'N/A')}</div>
        </div>
"""
        
        user_count = len([m for m in messages if m["role"] == "user"])
        assistant_count = len([m for m in messages if m["role"] == "assistant"])
        
        html_content += f"""
        <div class="stats">
            <h3>📊 Conversation Statistics</h3>
            <p><strong>Total Messages:</strong> {len(messages)}</p>
            <p><strong>Your Messages:</strong> {user_count}</p>
            <p><strong>Assistant Messages:</strong> {assistant_count}</p>
            <p><strong>Conversation Duration:</strong> {self._calculate_duration(messages)}</p>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by AI Chatbot Pro | Made with ❤️ by Kavya Rajeev</p>
    </div>
</body>
</html>
"""
        
        return html_content, "text/html"
    
    # def _export_pdf(self, messages: List[Dict], conversation_id: str) -> Tuple[str, str]:
    #     """Export as PDF (using HTML to PDF conversion)"""
    #     try:
    #         # Try to use weasyprint for PDF generation
            
            
    #         html_content, _ = self._export_html(messages, conversation_id)
    #         pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
            
    #         return pdf_bytes, "application/pdf"
            
    #     except ImportError:
    #         # Fallback: Return HTML with PDF mime type
    #         html_content, _ = self._export_html(messages, conversation_id)
    #         return html_content, "text/html"
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        import html
        return html.escape(text)
    
    def _calculate_duration(self, messages: List[Dict]) -> str:
        """Calculate conversation duration"""
        if len(messages) < 2:
            return "N/A"
        
        try:
            first_time = messages[0].get("timestamp", "00:00")
            last_time = messages[-1].get("timestamp", "00:00")
            
            # Simple time difference calculation (assumes same day)
            first_parts = first_time.split(":")
            last_parts = last_time.split(":")
            
            first_minutes = int(first_parts[0]) * 60 + int(first_parts[1])
            last_minutes = int(last_parts[0]) * 60 + int(last_parts[1])
            
            duration = last_minutes - first_minutes
            if duration < 0:
                duration += 24 * 60  # Handle day rollover
            
            hours = duration // 60
            minutes = duration % 60
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
                
        except:
            return "N/A"
    
    def get_conversation_summary(self, messages: List[Dict]) -> Dict:
        """Generate conversation summary statistics"""
        if not messages:
            return {}
        
        user_messages = [m for m in messages if m["role"] == "user"]
        assistant_messages = [m for m in messages if m["role"] == "assistant"]
        
        total_words = sum(len(m["content"].split()) for m in messages)
        total_chars = sum(len(m["content"]) for m in messages)
        
        return {
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "total_words": total_words,
            "total_characters": total_chars,
            "avg_words_per_message": total_words / len(messages) if messages else 0,
            "conversation_duration": self._calculate_duration(messages),
            "first_message_time": messages[0].get("timestamp", "N/A"),
            "last_message_time": messages[-1].get("timestamp", "N/A")
        }
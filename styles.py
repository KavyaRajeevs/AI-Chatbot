# styles.py

def get_chat_styles():
    return {
        "user_message": {
            "background": "#DCF8C6",
            "color": "#000000",
            "padding": "10px",
            "border_radius": "8px",
            "margin": "5px 0",
            "align": "right"
        },
        "bot_message": {
            "background": "#F1F0F0",
            "color": "#000000",
            "padding": "10px",
            "border_radius": "8px",
            "margin": "5px 0",
            "align": "left"
        },
        "chat_window": {
            "background": "#FFFFFF",
            "padding": "20px",
            "border_radius": "10px",
            "box_shadow": "0 2px 8px rgba(0,0,0,0.1)"
        },
        "input_box": {
            "background": "#F9F9F9",
            "padding": "10px",
            "border_radius": "8px",
            "border": "1px solid #E0E0E0"
        }
    }
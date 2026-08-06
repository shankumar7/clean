"""
Theme definitions and color palettes for Light & Dark mode support.
"""

DARK_THEME = {
    "mode": "dark",
    "bg": "#0f172a",
    "card_bg": "rgba(30, 41, 59, 0.85)",
    "card_border": "rgba(255, 255, 255, 0.1)",
    "text_primary": "#ffffff",
    "text_secondary": "#94a3b8",
    "accent": "#38bdf8",
    "header_bg": "rgba(30, 41, 59, 0.9)",
    "tab_bg": "#1e293b",
    "tab_text": "#94a3b8",
    "tab_selected_bg": "#38bdf8",
    "tab_selected_text": "#0f172a",
    "log_bg": "#090d16",
    "log_text": "#38bdf8",
    "chart_bg": "#0f172a",
    "chart_fg": "#94a3b8"
}

LIGHT_THEME = {
    "mode": "light",
    "bg": "#f1f5f9",
    "card_bg": "#ffffff",
    "card_border": "#cbd5e1",
    "text_primary": "#0f172a",
    "text_secondary": "#475569",
    "accent": "#0284c7",
    "header_bg": "#ffffff",
    "tab_bg": "#e2e8f0",
    "tab_text": "#475569",
    "tab_selected_bg": "#0284c7",
    "tab_selected_text": "#ffffff",
    "log_bg": "#ffffff",
    "log_text": "#0284c7",
    "chart_bg": "#ffffff",
    "chart_fg": "#475569"
}


class ThemeManager:
    _current_theme = DARK_THEME
    _listeners = []

    @classmethod
    def get_theme(cls):
        return cls._current_theme

    @classmethod
    def is_dark(cls):
        return cls._current_theme["mode"] == "dark"

    @classmethod
    def toggle_theme(cls):
        if cls._current_theme["mode"] == "dark":
            cls._current_theme = LIGHT_THEME
        else:
            cls._current_theme = DARK_THEME
        
        cls._notify_listeners()
        return cls._current_theme

    @classmethod
    def set_theme(cls, mode):
        if mode == "light":
            cls._current_theme = LIGHT_THEME
        else:
            cls._current_theme = DARK_THEME
        cls._notify_listeners()

    @classmethod
    def register_listener(cls, callback):
        if callback not in cls._listeners:
            cls._listeners.append(callback)

    @classmethod
    def _notify_listeners(cls):
        for cb in list(cls._listeners):
            try:
                cb(cls._current_theme)
            except Exception as e:
                print(f"[ThemeManager] Error notifying theme listener: {e}")

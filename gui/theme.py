"""
Enhanced Theme definitions and color palettes for Light & Dark mode support.
"""

DARK_THEME = {
    "mode": "dark",
    "bg": "#0b132b",
    "card_bg": "rgba(28, 37, 65, 0.85)",
    "card_border": "rgba(255, 255, 255, 0.12)",
    "text_primary": "#ffffff",
    "text_secondary": "#8d99ae",
    "accent": "#00b4d8",
    "accent_glow": "#90e0ef",
    "header_bg": "rgba(11, 19, 43, 0.95)",
    "tab_bg": "#1c2541",
    "tab_text": "#8d99ae",
    "tab_selected_bg": "#00b4d8",
    "tab_selected_text": "#0b132b",
    "log_bg": "#060a17",
    "log_text": "#38bdf8",
    "chart_bg": "#0b132b",
    "chart_fg": "#8d99ae",
    "btn_bg": "#3a506b",
    "btn_text": "#ffffff"
}

LIGHT_THEME = {
    "mode": "light",
    "bg": "#f8fafc",
    "card_bg": "#ffffff",
    "card_border": "#e2e8f0",
    "text_primary": "#0f172a",
    "text_secondary": "#64748b",
    "accent": "#0284c7",
    "accent_glow": "#0077b6",
    "header_bg": "#ffffff",
    "tab_bg": "#e2e8f0",
    "tab_text": "#64748b",
    "tab_selected_bg": "#0284c7",
    "tab_selected_text": "#ffffff",
    "log_bg": "#ffffff",
    "log_text": "#0284c7",
    "chart_bg": "#ffffff",
    "chart_fg": "#64748b",
    "btn_bg": "#cbd5e1",
    "btn_text": "#0f172a"
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

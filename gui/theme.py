"""
Comprehensive Theme definitions and high-contrast color palettes for Light & Dark mode.
"""

DARK_THEME = {
    "mode": "dark",
    "bg": "#0b132b",
    "card_bg": "#1c2541",
    "card_border": "#2e3b5e",
    "text_primary": "#ffffff",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "accent": "#38bdf8",
    "header_bg": "#141c33",
    "tab_bg": "#1e293b",
    "tab_text": "#94a3b8",
    "tab_selected_bg": "#0284c7",
    "tab_selected_text": "#ffffff",
    "log_bg": "#060a17",
    "log_text": "#38bdf8",
    "chart_bg": "#0b132b",
    "chart_fg": "#94a3b8",
    "input_bg": "#0f172a",
    "input_text": "#ffffff",
    "notice_bg": "rgba(2, 132, 199, 0.25)",
    "notice_text": "#f8fafc",
    "warning_bg": "rgba(239, 68, 68, 0.25)",
    "warning_text": "#fee2e2"
}

LIGHT_THEME = {
    "mode": "light",
    "bg": "#f1f5f9",
    "card_bg": "#ffffff",
    "card_border": "#cbd5e1",
    "text_primary": "#0f172a",
    "text_secondary": "#334155",
    "text_muted": "#64748b",
    "accent": "#0284c7",
    "header_bg": "#ffffff",
    "tab_bg": "#e2e8f0",
    "tab_text": "#475569",
    "tab_selected_bg": "#0284c7",
    "tab_selected_text": "#ffffff",
    "log_bg": "#ffffff",
    "log_text": "#0284c7",
    "chart_bg": "#ffffff",
    "chart_fg": "#334155",
    "input_bg": "#f8fafc",
    "input_text": "#0f172a",
    "notice_bg": "#e0f2fe",
    "notice_text": "#0369a1",
    "warning_bg": "#fee2e2",
    "warning_text": "#991b1b"
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

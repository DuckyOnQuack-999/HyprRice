class WindowManager:
    def __init__(self, config_path):
        self.config_path = config_path
    def get_window_config(self):
        return {}
    def set_window_config(self, config):
        pass
    def apply_window_config(self, config):
        pass
    def set_window_opacity(self, opacity):
        pass
    def set_border_size(self, size):
        pass
    def set_border_color(self, color):
        pass
    def set_gaps(self, gaps_in, gaps_out):
        pass
    def toggle_smart_gaps(self, enabled):
        pass
    def toggle_blur(self, enabled):
        pass
    def set_blur_size(self, size):
        pass
    def get_window_list(self):
        return []
    def focus_window(self, window_address):
        pass
    def close_window(self, window_address):
        pass
    def toggle_floating(self, window_address):
        pass
    def set_window_opacity_rule(self, window_class, opacity):
        pass
    def get_window_rules(self):
        return [] 
class InputManager:
    def __init__(self, config_path):
        self.config_path = config_path
    def get_input_config(self):
        return {}
    def set_input_config(self, config):
        pass
    def apply_input_config(self, config):
        pass
    def set_keyboard_repeat_rate(self, rate):
        pass
    def set_keyboard_repeat_delay(self, delay):
        pass
    def set_mouse_sensitivity(self, sensitivity):
        pass
    def set_mouse_accel_profile(self, profile):
        pass
    def toggle_touchpad_natural_scroll(self, enabled):
        pass
    def toggle_touchpad_tap_to_click(self, enabled):
        pass
    def get_input_devices(self):
        return [] 
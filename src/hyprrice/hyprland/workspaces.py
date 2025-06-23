class WorkspaceManager:
    def __init__(self, config_path):
        self.config_path = config_path
    def get_workspace_config(self):
        return {}
    def set_workspace_config(self, config):
        pass
    def get_workspaces(self):
        return []
    def switch_to_workspace(self, workspace_id):
        pass
    def move_to_workspace(self, workspace_id):
        pass
    def create_workspace(self, name):
        pass
    def rename_workspace(self, workspace_id, new_name):
        pass
    def bind_workspace_to_monitor(self, workspace_id, monitor):
        pass
    def get_active_workspace(self):
        return None 
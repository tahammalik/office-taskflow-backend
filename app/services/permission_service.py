PERMISSIONS = {
    "admin": {
        "workspace": {"create", "read", "update", "delete"},
        "team": {"create", "read", "update", "delete"},
        "project": {"create", "read", "update", "delete"},
        "task": {"create", "read", "update", "delete"},
    },

    "manager": {
        "workspace": {"read", "update"},
        "team": {"create", "read", "update"},
        "project": {"create", "read", "update"},
        "task": {"create", "read", "update"},
    },

    "leader": {
        "workspace": {"read"},
        "team": {"read", "update"},
        "project": {"read", "update"},
        "task": {"create", "read", "update"},
    },

    "employee": {
        "workspace": {"read"},
        "team": {"read"},
        "project": {"read"},
        "task": {"create", "read", "update"},
    },
}

class PermissionService:
    def __init__(self):
        pass
    @staticmethod
    def has_permission(role:str, resource_type:str, action:str):
        role_permission = PERMISSIONS.get(role)

        if not role_permission:
            return False

        action_permission = role_permission.get(resource_type,set())

        return action in action_permission


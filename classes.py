class User:
    def __init__(self, first_name, last_name, user_id):
        self.first_name = first_name
        self.last_name = last_name
        self.id = user_id

class Resource:
        def __init__(self, name, resource_type):
            self.name = name
            self.type = resource_type  # Data Center or Server Rack


Unknown = User('Unknown', '', '')
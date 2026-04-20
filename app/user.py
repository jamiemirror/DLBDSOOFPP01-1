class User:
    """user of the application"""
    name: str
    def __init__(self):
        self.name = "User"
        
    def canDelete() -> bool:
        """check if a the user is administrator"""
        return False

class Admin(User):
    def __init__(self):
        self.name = "Administrator"
    
    def canDelete() -> bool:
        """check if a the user is administrator, only administrators can delete habits"""
        return True

#just an idea to extend with future user logins: UserGroup class
class UserGroup:
    def __init__(self, group_name):
        self.group_name = group_name
        self.users = []

    def add_user(self, user):
        if isinstance(user, User):
            self.users.append(user)
            print(f"{user.username} has been added to the group {self.group_name}.")
        else:
            print("Only User objects can be added to the group.")

    def remove_user(self, user):
        if user in self.users:
            self.users.remove(user)
            print(f"{user.username} has been removed from the group {self.group_name}.")
        else:
            print(f"{user.username} is not in the group.")

    def list_users(self):
        if not self.users:
            print(f"No users in the group {self.group_name}.")
        else:
            print(f"Users in the group {self.group_name}:")
            for user in self.users:
                print(user)

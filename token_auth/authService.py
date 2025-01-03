
class UserAuthentication():
    @classmethod
    def verifyUser(cls, userCredentials):
        try:
            authenticatedUser = None
            dataBaseUsers = Usuarios.objects.values()
        except:
            print("Error")

print(UserAuthentication.verifyUser("User"))
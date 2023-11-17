
class UserAuthentication():
    @classmethod
    def verifyUser(cls, userCredentials):
        try:
            authenticatedUser = None
            dataBaseUsers = Usuarios.objects.values()
            print(dataBaseUsers)
        except:
            print("Holi")

print(UserAuthentication.verifyUser("User"))
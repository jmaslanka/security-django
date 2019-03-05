from django.contrib.auth.hashers import Argon2PasswordHasher


class Argon2PasswordHasher(Argon2PasswordHasher):
    time_cost = 10  # Default 2
    memory_cost = 4096  # Default 512
    parallelism = 2

    def encode(self, password, salt):
        argon2 = self._load_library()
        data = argon2.low_level.hash_secret(
            password.encode(),
            salt.encode(),
            time_cost=self.time_cost,
            memory_cost=self.memory_cost,
            parallelism=self.parallelism,
            hash_len=40,  # Default 16
            type=argon2.low_level.Type.I,
        )

        return self.algorithm + data.decode('ascii')

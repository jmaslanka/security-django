from django.contrib.auth.hashers import Argon2PasswordHasher


class Argon2PasswordHasher(Argon2PasswordHasher):
    """
    - increase the default values for time cost and memory usage
    - change the algorithm type from Argon2i to Argon2d
    """
    time_cost = 3  # Default 2
    memory_cost = 2**16  # Default 2**9, 64MB instead of 512KB
    parallelism = 2

    def encode(self, password, salt):
        argon2 = self._load_library()
        data = argon2.low_level.hash_secret(
            password.encode(),
            salt.encode(),
            time_cost=self.time_cost,
            memory_cost=self.memory_cost,
            parallelism=self.parallelism,
            hash_len=argon2.DEFAULT_HASH_LENGTH,
            type=argon2.low_level.Type.D,
        )
        return self.algorithm + data.decode('ascii')

    def verify(self, password, encoded):
        argon2 = self._load_library()
        algorithm, rest = encoded.split('$', 1)
        assert algorithm == self.algorithm
        try:
            return argon2.low_level.verify_secret(
                ('$' + rest).encode('ascii'),
                password.encode(),
                type=argon2.low_level.Type.D,
            )
        except argon2.exceptions.VerificationError:
            return False

from decouple import config


postgresql_environ = {
    "USER": config('POSTGRES_USER'),
    "PASSWORD": config('POSTGRES_PASSWORD'),
    "HOST": config('POSTGRES_HOST'),
    "PORT": config('POSTGRES_PORT'),
    "DATABASE": config('POSTGRES_DATABASE')
}
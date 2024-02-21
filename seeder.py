from django_seed import Seed

seeder = Seed.seeder()

from users.models import CustomUser

seeder.add_entity(CustomUser, 5)
inserted_pks = seeder.execute()

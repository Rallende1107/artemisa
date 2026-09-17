# 1. Apagar el stack y BORRAR la base (volumen pgdata)
docker compose down -v

# 2. Vaciar media y dump (dejan de existir imágenes y archivos cargados)
rmdir /s /q media dump
mkdir media dump

# 3. Reconstruir la imagen sin caché y levantar
docker compose build --no-cache
docker compose up -d

# 4. Regenerar migraciones (una 0001 por app)
docker compose exec web python manage.py clear_migrations
docker compose exec web python manage.py makemigrations

# 5. Migrar, sembrar
docker compose exec web python manage.py initial_setup
# 5. Migrar, sembrar y crear usuarios de desarrollo
docker compose exec web python manage.py initial_setup --dev

# 6. Reiniciar worker y beat para que tomen el código y las tareas nuevas
docker compose restart worker beat web
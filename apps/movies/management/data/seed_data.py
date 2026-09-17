"""Datos iniciales de la app `movies` (los siembra `seed_movies`, idempotente y reejecutable)."""

default_movie_serie_genres = [
    {"name": "Unknown", "name_esp": "Desconocido", "description": "Género para trabajos cuyo género principal no está claro o no se ha especificado.", "explicit": False},
    {"name": "Action", "name_esp": "Acción", "description": "Historias que se centran en secuencias de lucha, persecuciones, violencia y emoción trepidante.", "explicit": False},
    {"name": "Adventure", "name_esp": "Aventura", "description": "Relatos que involucran viajes, exploración, búsqueda de tesoros, peligros y descubrimientos emocionantes.", "explicit": False},
    {"name": "Comedy", "name_esp": "Comedia", "description": "Relatos cuyo objetivo principal es provocar la risa y el humor en la audiencia.", "explicit": False},
    {"name": "Drama", "name_esp": "Drama", "description": "Historias que se centran en las emociones, conflictos internos y relaciones intensas entre personajes.", "explicit": False},
    {"name": "Fantasy", "name_esp": "Fantasía", "description": "Relatos que incorporan elementos mágicos, criaturas míticas, mundos imaginarios y sucesos sobrenaturales", "explicit": False},
    {"name": "Sci-Fi (Science Fiction)", "name_esp": "Ciencia Ficción", "description": "Relatos que exploran conceptos científicos y tecnológicos, viajes espaciales, futuros distópicos o utópicos, vida extraterrestre, etc.", "explicit": False},
    {"name": "Horror", "name_esp": "Terror", "description": "Historias diseñadas para asustar, inquietar o provocar miedo en la audiencia, a menudo con elementos sobrenaturales o violentos.", "explicit": False},
    {"name": "Mystery", "name_esp": "Misterio", "description": "Relatos que giran en torno a la resolución de un enigma, crimen o suceso inexplicable, manteniendo la intriga hasta el final.", "explicit": False},
    {"name": "Romance", "name_esp": "Romance", "description": "Historias que se centran en el desarrollo de relaciones amorosas y sentimentales entre personajes.", "explicit": False},
    {"name": "Thriller", "name_esp": "Suspenso", "description": "Generan tensión e incertidumbre en el espectador.", "explicit": False},
    {"name": "Animation", "name_esp": "Animación", "description": "Creadas mediante la técnica de animación.", "explicit": False},
    {"name": "Crime", "name_esp": "Crimen", "description": "Giran en torno a actividades delictivas y sus consecuencias.", "explicit": False},
    {"name": "Historical", "name_esp": "Histórico", "description": "Basadas en eventos o personajes del pasado.", "explicit": False},
    {"name": "Western", "name_esp": "Oeste", "description": "Ambientadas en el Viejo Oeste americano.", "explicit": False},
    {"name": "Family", "name_esp": "Familiar", "description": "Aptas para ser disfrutadas por toda la familia.", "explicit": False},
    {"name": "Melodrama", "name_esp": "Melodrama", "description": "", "explicit": False},
]

# movie_serie_types


default_movie_serie_types = [
    {"name": "Unknown", "name_esp": "Desconocido", "description": "Tipo de título desconocido."},
    {"name": "Documentary", "name_esp": "Documental", "description": "Presentan hechos reales con fines informativos o de análisis."},
    {"name": "Animated Feature Film", "name_esp": "Largometraje Animado", "description": "Presentan animación de larga duración."},
    {"name": "Live-Action Feature Film", "name_esp": "Largometraje de Acción Real", "description": "Presentan actores reales."},
    {"name": "Short Film", "name_esp": "Cortometraje", "description": "Corta duración."},
    {"name": "TV Movie", "name_esp": "Película para Televisión", "description": "Producidas para ser emitidas en televisión."},
    {"name": "Direct-to-Video", "name_esp": "Directo a Video", "description": "Lanzadas directamente en formato de video."},
    {"name": "Independent Film", "name_esp": "Película Independiente", "description": "Producidas fuera de los grandes estudios."},
    {"name": "Experimental Film", "name_esp": "Película Experimental", "description": "Desafían las convenciones narrativas y formales."},
]

# movie_serie_roles


default_movie_serie_roles = [
    {"name": "Lead", "name_esp": "Principal","description": "El actor o actriz que interpreta al personaje central de la historia.", "role_type": 20,},
    {"name": "Supporting", "name_esp": "Actor de Reparto","description": "Un actor o actrizque interpreta un personaje secundario importante.", "role_type": 20,},
    {"name": "Cameo", "name_esp": "Cameo","description": "Una aparición breve de una persona famosa.", "role_type": 20,},
    {"name": "Voice Actor", "name_esp": "Actor de Voz","description": "Un actor que proporciona la voz de un personaje animado o digital.", "role_type": 20,},
    {"name": "Narrator", "name_esp": "Narrador","description": "La voz en off que cuenta parte de la historia.", "role_type": 20,},
    {"name": "Extra", "name_esp": "Extra Destacado","description": "Un extra con una participación ligeramente más notable.", "role_type": 20,},
    {"name": "Director", "name_esp": "Director","description": "La persona responsable de la visión creativa general.", "role_type": 10,},
    {"name": "Screenwriter", "name_esp": "Guionista","description": "La persona que escribe el guion.", "role_type": 10,},
    {"name": "Producer", "name_esp": "Productor","description": "La persona responsable de la gestión y financiación.", "role_type": 10,},
    {"name": "Cinematographer", "name_esp": "Director de Fotografía","description": "La persona responsable de la filmación y el aspecto visual.", "role_type": 10,},
    {"name": "Film Editor", "name_esp": "Montajista","description": "La persona que ensambla las diferentes tomas.", "role_type": 10,},
    {"name": "Production Designer", "name_esp": "Diseñador de Producción","description": "La persona responsable del aspecto visual del set y los escenarios.", "role_type": 10,},
    {"name": "Costume Designer", "name_esp": "Diseñador de Vestuario","description": "La persona responsable del vestuario de los personajes.", "role_type": 10,},
    {"name": "Composer", "name_esp": "Compositor","description": "La persona que escribe la música original.", "role_type": 10,},
    {"name": "Sound Designer", "name_esp": "Diseñador de Sonido","description": "La persona responsable del diseño y la mezcla del sonido.", "role_type": 10,},
    {"name": "Art Director", "name_esp": "Director de Arte","description": "La persona responsable de la supervisión de los aspectos visuales.", "role_type": 10,},
    {"name": "Casting Director", "name_esp": "Director de Casting","description": "La persona responsable de seleccionar a los actores para los roles.", "role_type": 10,},
    {"name": "Visual Effects Supervisor", "name_esp": "Supervisor de Efectos Visuales","description": "La persona responsable de la creación de los efectos visuales.", "role_type": 10,},
]

# movie_ratings


default_movie_ratings = [
    {"acronym": "UNK", "name": "Unknown", "name_esp": "Desconocido", "description": "Clasificación desconocida o no especificada."},
    {"acronym": "G", "name": "All Ages.", "name_esp": "Todas las Edades.", "description": "Se admiten todas las edades. \nNo se permite que los niños vean nada que pueda ofender a los padres."},
    {"acronym": "PG", "name": "Children Parental Guidance Suggested.", "name_esp": "Niños Guía Paterna Sugerida.", "description": "Contenido apto para niños. \nAlgunos materiales pueden no ser adecuados para niños.\nSe recomienda a los padres que brinden \"orientación parental\". Puede contener material que a los padres no les guste para sus hijos pequeños."},
    {"acronym": "PG-13", "name": "Teens 13 or older Parents Strongly Cautioned", "name_esp": "Adolescentes de 13 años o más Guía Paterna Estricta", "description": "Contenido apto para adolescentes de 13 años o más.\nAlgunos materiales pueden ser inapropiados para niños menores de 13 años.\nSe recomienda a los padres que tengan cuidado. Algunos materiales pueden ser inapropiados para preadolescentes."},
    {"acronym": "R", "name": "Restricted", "name_esp": "Restringido", "description": "Los menores de 17 años deben ir acompañados de un padre o tutor adulto.\nContiene material para adultos.\nSe recomienda a los padres que se informen más sobre la película antes de llevar a sus hijos pequeños con ellos."},
    {"acronym": "NC-17", "name": "Adults Only", "name_esp": "Solo Adultos", "description": "No Apta para Menores de 17 años.\nContiene material explícito para adultos."},
]

# movie_companies


# serie_ratings

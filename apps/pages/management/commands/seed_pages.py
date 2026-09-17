"""seed_pages — contenido inicial de las páginas informativas (Nosotros, Términos de
uso, Privacidad). Idempotente: crea cada sección por (página, título) si no existe y
NO pisa lo editado desde el panel. Antes vivía en una migración de datos de system."""
from django.core.management.base import BaseCommand

from apps.pages.models import AboutSection, PrivacySection, TermsSection


MODELOS = {"nosotros": AboutSection, "terminos": TermsSection, "privacidad": PrivacySection}

# (página, orden, título, contenido)
SECCIONES = [
    ('nosotros', 10, 'Qué es Frikiverso',
     'Frikiverso es un catálogo de anime, manga, series, películas, música y visual novels, y a la vez tu tracker personal: cada título puede entrar a tu colección con estado, puntuación y favoritos, al estilo de MyAnimeList o Letterboxd.\n\nNace como proyecto personal: un solo lugar para todo lo que vemos, leemos, jugamos y escuchamos.'),
    ('nosotros', 20, 'Qué encontrarás',
     "Cada medio tiene su sección con catálogo filtrable (género, año, tipo, estudio, productora…), fichas detalladas y filas de recientes y favoritos.\n\n- Anime y manga, con sus personajes, estudios, productoras y revistas.\n- Películas y series, con reparto, equipo, productoras y distribuidoras.\n- Visual novels y juegos Ren'Py, con sus creadores y editoras.\n- Música: artistas, álbumes y canciones con sus letras.\n- Tu colección: estados por medio, notas y favoritos."),
    ('nosotros', 30, 'Todo conectado',
     'El corazón del sitio es el cruce de datos: desde una película llegas a su directora, de ahí a sus otras películas; desde un anime a su estudio y a todos los animes del estudio; desde un personaje a su actor de voz. Cada nombre que veas es, casi siempre, un enlace.'),
    ('nosotros', 40, 'Fuentes de datos',
     'La información de catálogo se importa y cura desde fuentes públicas: MyAnimeList (anime y manga), VNDB (visual novels) y Deezer (música). Se muestra con fines informativos y de referencia; los derechos pertenecen a sus titulares.'),
    ('nosotros', 50, 'Tecnología',
     'Construido con Django y Python, con un panel de gestión propio para curar el catálogo. El diseño es propio, oscuro y con acento neón, pensado para pantallas grandes y para el celular.'),
    ('nosotros', 60, 'Contacto',
     '¿Sugerencias, errores, títulos que faltan? Escríbenos desde la página de contacto — cada mensaje se lee.'),
    ('terminos', 10, 'Aceptación',
     'Al acceder y utilizar Frikiverso aceptas estos Términos de uso. Si no estás de acuerdo con alguna parte, te pedimos que no utilices el sitio.\n\nEl uso continuado tras un cambio de los términos implica la aceptación de la versión vigente.'),
    ('terminos', 20, 'Uso del sitio',
     'Frikiverso es un catálogo informativo y una herramienta personal de colección. Te comprometes a un uso personal y no comercial.\n\nEn particular, no está permitido:\n\n- Dañar, sobrecargar o interferir con el servicio.\n- Extraer datos de forma automatizada (scraping) sin autorización.\n- Revender o redistribuir el contenido del catálogo.\n- Intentar acceder a cuentas o áreas de administración ajenas.'),
    ('terminos', 30, 'Propiedad y datos',
     'Los títulos, portadas, nombres y marcas pertenecen a sus respectivos autores y titulares. La información se muestra con fines informativos y de referencia (MyAnimeList, VNDB, Deezer).\n\nSi eres titular de derechos y quieres que retiremos un contenido, escríbenos por la página de contacto y lo revisaremos.'),
    ('terminos', 40, 'Cuentas',
     'Para usar la colección personal necesitas una cuenta. Eres responsable de la confidencialidad de tus credenciales y de la actividad bajo tu cuenta.\n\nPodemos suspender cuentas que incumplan estos términos o dañen el servicio.'),
    ('terminos', 50, 'Tu colección',
     'Tus listas, estados, puntuaciones y notas te pertenecen. Nos concedes permiso para almacenarlas y mostrártelas dentro del sitio; no las publicamos a otros usuarios sin que tú lo actives.\n\nPuedes quitar cualquier título de tu colección cuando quieras.'),
    ('terminos', 60, 'Cambios del servicio',
     'Frikiverso está en desarrollo activo: las funciones pueden cambiar, aparecer o retirarse. Intentaremos avisar los cambios relevantes en el propio sitio.'),
    ('terminos', 70, 'Responsabilidad',
     'El sitio se ofrece «tal cual», sin garantías sobre la exactitud o disponibilidad de la información.\n\nLos enlaces a sitios de terceros se ofrecen como referencia; no controlamos su contenido ni sus políticas.'),
    ('terminos', 80, 'Contacto',
     'Cualquier duda sobre estos términos: escríbenos desde la página de contacto.'),
    ('privacidad', 10, 'Resumen',
     'Guardamos lo mínimo para que el sitio funcione: tu cuenta, tu colección y los mensajes que nos envías. No vendemos datos ni usamos rastreadores de terceros.'),
    ('privacidad', 20, 'Qué recopilamos',
     'Solo lo que tú creas al usar el sitio:\n\n- Cuenta: nombre de usuario y correo electrónico.\n- Colección: títulos añadidos, estados, puntuaciones, favoritos y notas.\n- Contacto: los mensajes que envías por el formulario.'),
    ('privacidad', 30, 'Para qué lo usamos',
     'Para operar el sitio: iniciar tu sesión, mostrarte tu colección y responder a tus mensajes. Nada más.'),
    ('privacidad', 40, 'Cookies y preferencias',
     'Usamos una cookie de sesión (imprescindible para el login) y almacenamiento local del navegador para preferencias de interfaz (vista de lista o tarjetas, filtros abiertos, pestaña elegida).\n\nNo hay cookies de publicidad ni analítica de terceros.'),
    ('privacidad', 50, 'Almacenamiento y seguridad',
     'Las contraseñas se guardan cifradas (hash), nunca en texto plano. El acceso a los datos está restringido a la administración del sitio.'),
    ('privacidad', 60, 'Terceros y fuentes',
     'La información del catálogo proviene de fuentes públicas (MyAnimeList, VNDB, Deezer). Tus datos personales no se comparten con esas fuentes ni con nadie.'),
    ('privacidad', 70, 'Tus derechos',
     'Puedes ver y corregir tus datos desde tu perfil, y pedir la eliminación de tu cuenta escribiéndonos por contacto: se borra la cuenta y su colección.'),
    ('privacidad', 80, 'Cambios de esta política',
     'Si esta política cambia, la fecha de «última actualización» lo reflejará y avisaremos en el sitio si el cambio es relevante.'),

]


class Command(BaseCommand):
    help = "Carga las secciones base de Nosotros, Términos y Privacidad (idempotente)."

    def handle(self, *args, **opts):
        creadas = respetadas = 0
        for pagina, orden, titulo, cuerpo in SECCIONES:
            _, creado = MODELOS[pagina].objects.get_or_create(
                title=titulo, defaults={"order": orden, "body": cuerpo, "is_active": True})
            creadas += creado
            respetadas += not creado
        self.stdout.write((
            f"  Páginas: secciones creadas={creadas} respetadas={respetadas}"))

"""
seed_mailing — carga las plantillas de correo base (idempotente).

Se ejecuta con el seed base (lo llama `init`) o suelto:
    python manage.py seed_mailing
    python manage.py seed_mailing --force   # sobrescribe las editadas a mano

Idempotente: `update_or_create` por `key`. Sin --force, respeta las plantillas
que ya existen (no pisa tus ediciones); con --force, las restaura a la base.
"""
from django.core.management.base import BaseCommand

from apps.mailing.models import EmailTemplate


def _card(titulo, cuerpo_html):
    """CONTENIDO de un correo: título + párrafos (+ botón). La maqueta (cabecera, fondo, pie y firma) la
    pone apps/mailing/layout.py al enviar y en la vista previa, así las plantillas no cargan estilos de fondo."""
    return (
        f'<h1 style="margin:0 0 14px;font-size:22px;line-height:30px;color:#0a0a0f">{titulo}</h1>'
        f'{cuerpo_html}'
    )


_BTN = ('<p style="margin:24px 0 18px"><a href="{{{{ {var} }}}}" style="display:inline-block;background:#00c8e0;'
        'color:#0a0a0f;text-decoration:none;padding:12px 24px;border-radius:8px;'
        'font-weight:bold;font-size:14px">{texto}</a></p>')


# key → (name, subject, body_html, body_text, description)
PLANTILLAS = {
    "bienvenida": (
        "Bienvenida", "¡Bienvenido a {{ sitio }}, {{ usuario }}!",
        _card("¡Bienvenido a {{ sitio }}!",
              "<p>Hola <strong>{{ usuario }}</strong>, tu cuenta ya está activa.</p>"
              "<p>Explora anime, manga, música, películas, series y juegos, y arma tu colección.</p>"
              + _BTN.format(var="enlace", texto="Ir a {{ sitio }}")),
        "Hola {{ usuario }}, bienvenido a {{ sitio }}. Entra en {{ enlace }}.",
        "Registro de usuario. Variables: usuario, sitio, enlace.",
    ),
    "contacto_aviso": (
        "Aviso de contacto", "📬 {{ nombre }} te escribió por contacto — {{ asunto }}",
        _card("{{ nombre }} te escribió por contacto",
              "<p><strong>Nombre:</strong> {{ nombre }}<br>"
              "<strong>Correo:</strong> <a href='mailto:{{ email }}' style='color:#00a9bd'>{{ email }}</a><br>"
              "<strong>Asunto:</strong> {{ asunto }}</p>"
              "<div style='margin:14px 0;padding:14px;background:#f3f4f8;border:1px solid #e3e6ee;"
              "border-radius:8px;white-space:pre-wrap;color:#1c1f2a'>{{ mensaje }}</div>"),
        "{{ nombre }} ({{ email }}) te escribió.\nAsunto: {{ asunto }}\n\n{{ mensaje }}",
        "Aviso al dueño cuando alguien usa el formulario de contacto. Variables: nombre, email, asunto, mensaje, sitio.",
    ),
    "password_reset": (
        "Recuperar contraseña", "Restablece tu contraseña · {{ sitio }}",
        _card("Restablece tu contraseña",
              "<p>Hola <strong>{{ usuario }}</strong>, recibimos una solicitud para restablecer tu contraseña.</p>"
              + _BTN.format(var="enlace", texto="Crear nueva contraseña")
              + "<p style='color:#a8a8b3;font-size:13px'>O copia: <span style='color:#00e5ff'>{{ enlace }}</span></p>"
              "<p style='color:#7a7a8c;font-size:12px'>Si no fuiste tú, ignora este correo.</p>"),
        "Hola {{ usuario }}, restablece tu contraseña: {{ enlace }}",
        "Auto-servicio «¿olvidaste tu contraseña?». Variables: usuario, sitio, enlace.",
    ),
    "password_changed": (
        "Contraseña cambiada", "Tu contraseña fue cambiada · {{ sitio }}",
        _card("Tu contraseña fue cambiada",
              "<p>Hola <strong>{{ usuario }}</strong>, tu contraseña en {{ sitio }} se cambió correctamente.</p>"
              "<p style='color:#7a7a8c;font-size:12px'>Si <strong>no fuiste tú</strong>, contáctanos de inmediato y restablece tu contraseña.</p>"),
        "Hola {{ usuario }}, tu contraseña en {{ sitio }} se cambió. Si no fuiste tú, contáctanos.",
        "Aviso de seguridad tras cambiar la contraseña. Variables: usuario, sitio.",
    ),
    "usuario_created": (
        "Cuenta creada", "Cuenta creada · {{ sitio }}",
        _card("Cuenta creada", "<p>Hola <strong>{{ usuario }}</strong>, un administrador creó tu cuenta en {{ sitio }}. Ya puedes iniciar sesión.</p>"),
        "Hola {{ usuario }}, tu cuenta en {{ sitio }} fue creada.",
        "Admin crea usuario. Variables: usuario, sitio, actor.",
    ),
    "usuario_activated": (
        "Cuenta activada", "Cuenta activada · {{ sitio }}",
        _card("Cuenta activada", "<p>Hola <strong>{{ usuario }}</strong>, tu cuenta en {{ sitio }} fue activada. Ya puedes volver a entrar.</p>"),
        "Hola {{ usuario }}, tu cuenta en {{ sitio }} fue activada.",
        "Activación de usuario. Variables: usuario, sitio, actor.",
    ),
    "usuario_bloqueado": (
        "Cuenta bloqueada", "Cuenta bloqueada · {{ sitio }}",
        _card("Cuenta bloqueada", "<p>Hola <strong>{{ usuario }}</strong>, tu cuenta en {{ sitio }} fue bloqueada. Si crees que es un error, contáctanos.</p>"),
        "Hola {{ usuario }}, tu cuenta en {{ sitio }} fue bloqueada.",
        "Bloqueo de usuario. Variables: usuario, sitio, actor.",
    ),
    "usuario_password_reset": (
        "Contraseña restablecida (admin)", "Contraseña restablecida · {{ sitio }}",
        _card("Contraseña restablecida", "<p>Hola <strong>{{ usuario }}</strong>, un administrador restableció tu contraseña en {{ sitio }}. Usa «¿Olvidaste tu contraseña?» para definir una nueva.</p>"),
        "Hola {{ usuario }}, un admin restableció tu contraseña en {{ sitio }}.",
        "Reset por admin. Variables: usuario, sitio, actor.",
    ),
    "usuario_deleted": (
        "Cuenta eliminada", "Cuenta eliminada · {{ sitio }}",
        _card("Cuenta eliminada", "<p>Hola <strong>{{ usuario }}</strong>, tu cuenta en {{ sitio }} fue eliminada. Gracias por haber pasado por aquí.</p>"),
        "Hola {{ usuario }}, tu cuenta en {{ sitio }} fue eliminada.",
        "Eliminación de usuario. Variables: usuario, sitio, actor.",
    ),
    "contacto_respuesta": (
        "Respuesta a tu mensaje de contacto", "Te respondimos: {{ asunto }} · {{ sitio }}",
        _card("Respondimos tu mensaje",
              "<p>Hola <strong>{{ nombre }}</strong>:</p>"
              "<p>Respondimos tu mensaje «{{ asunto }}»:</p>"
              "<blockquote style='border-left:3px solid #00e5ff;padding-left:12px;color:#a8a8b3'>"
              "{{ respuesta|linebreaksbr }}</blockquote>"
              + _BTN.format(var="enlace", texto="Ver el hilo en Mis mensajes")),
        "Hola {{ nombre }}, respondimos tu mensaje «{{ asunto }}»:\n\n{{ respuesta }}\n\nHilo completo: {{ enlace }}",
        "Se envía al usuario cuando el staff responde su mensaje de contacto. Variables: nombre, asunto, respuesta, enlace, sitio.",
    ),
}


class Command(BaseCommand):
    help = "Carga las plantillas de correo base (idempotente)."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Sobrescribe las plantillas ya existentes.")

    def handle(self, *args, **opts):
        creadas = actualizadas = respetadas = 0
        for key, (name, subject, body_html, body_text, desc) in PLANTILLAS.items():
            existe = EmailTemplate.objects.filter(key=key).first()
            if existe and not opts["force"]:
                respetadas += 1
                continue
            _, creado = EmailTemplate.objects.update_or_create(
                key=key,
                defaults=dict(name=name, subject=subject, body_html=body_html,
                              body_text=body_text, description=desc, is_active=True),
            )
            creadas += creado
            actualizadas += not creado
        self.stdout.write((
            f"  Plantillas de correo: creadas={creadas} actualizadas={actualizadas} respetadas={respetadas}"
        ))

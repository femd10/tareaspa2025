from flask import Flask, render_template, request, redirect, url_for, session, send_file
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import random
import io

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesiones'

# --- Rutinas disponibles ---
rutinas_posibles = [
    {
        "nombre": "Rutina 1 - Full Body",
        "descripcion": "Ejercita todo el cuerpo con diferentes combinaciones.",
        "tipo": "ganar musculo",
        "ejercicios": ["Sentadillas", "Press banca", "Remo", "Peso muerto", "Plancha", "Flexiones"]
    },
    {
        "nombre": "Rutina 2 - Fuerza Total",
        "descripcion": "Rutina centrada en ejercicios compuestos y fuerza máxima.",
        "tipo": "ganar musculo",
        "ejercicios": ["Peso muerto", "Press militar", "Dominadas", "Fondos", "Curl bíceps", "Press banca"]
    },
    {
        "nombre": "Rutina 3 - Cardio y Resistencia",
        "descripcion": "Ideal para mejorar resistencia y capacidad pulmonar.",
        "tipo": "adelgazar",
        "ejercicios": ["Correr", "Burpees", "Bicicleta", "Escaladores", "Cuerda", "Caminata rápida"]
    },
    {
        "nombre": "Rutina 4 - HIIT Intenso",
        "descripcion": "Alta intensidad para quemar grasa en poco tiempo.",
        "tipo": "adelgazar",
        "ejercicios": ["Burpees", "Saltos", "Plancha", "Flexiones", "Correr", "Mountain climbers"]
    },
    {
        "nombre": "Rutina 5 - Funcional",
        "descripcion": "Entrenamiento con fuerza, equilibrio y movilidad.",
        "tipo": "ganar musculo",
        "ejercicios": ["Zancadas", "Kettlebell swings", "Burpees", "Plancha lateral", "Flexiones", "Correr 15 min"]
    },
    {
        "nombre": "Rutina 6 - Calistenia",
        "descripcion": "Usa tu peso corporal para definir y tonificar.",
        "tipo": "adelgazar",
        "ejercicios": ["Dominadas", "Flexiones", "Fondos", "Abdominales", "Plancha", "Sentadillas con salto"]
    }
]


@app.route('/', methods=['GET', 'POST'])
def inscripcion():
    if request.method == 'POST':
        nombre = request.form['nombre']
        edad = request.form['edad']
        dias_usuario = int(request.form['dias'])
        tipo = request.form['tipo']

        # Filtrar rutinas por tipo elegido
        rutinas_filtradas = [r for r in rutinas_posibles if r['tipo'] == tipo]

        # Escoger una rutina aleatoria
        rutina = random.choice(rutinas_filtradas)

        # Número de días aleatorio entre 3 y 6
        dias_rutina = random.randint(3, 6)

        # Crear plan con 3 ejercicios aleatorios por día
        plan = {}
        for i in range(1, dias_rutina + 1):
            plan[f"Día {i}"] = random.sample(rutina["ejercicios"], k=3)

        # Guardar en sesión
        session['datos_usuario'] = {
            'nombre': nombre,
            'edad': edad,
            'tipo': tipo,
            'dias_usuario': dias_usuario,
            'dias_rutina': dias_rutina,
            'rutina': rutina,
            'plan': plan
        }

        return redirect(url_for('confirmacion'))

    return render_template('index.html')


@app.route('/confirmacion')
def confirmacion():
    datos = session.get('datos_usuario')
    if not datos:
        return redirect(url_for('inscripcion'))
    return render_template('confirmacion.html', **datos)


@app.route('/descargar_pdf')
def descargar_pdf():
    datos = session.get('datos_usuario')
    if not datos:
        return redirect(url_for('inscripcion'))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # ---- Estilos personalizados ----
    titulo = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor("#2E86C1"),
        alignment=1,
        spaceAfter=20
    )

    subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        textColor=colors.HexColor("#117A65"),
        fontSize=14,
        spaceAfter=10
    )

    texto = ParagraphStyle(
        'Texto',
        parent=styles['BodyText'],
        fontSize=11,
        leading=14
    )

    # ---- Logo (opcional) ----
    try:
        logo = Image("static/logo.png", width=60, height=60)
        logo.hAlign = 'CENTER'
        elements.append(logo)
    except:
        pass

    # ---- Encabezado ----
    elements.append(Paragraph("🏋️ Gimnasio VitalForce", titulo))
    elements.append(Paragraph("Rutina Personalizada de Entrenamiento", subtitulo))
    elements.append(Spacer(1, 10))

    # ---- Datos del usuario ----
    datos_tabla = [
        ["Nombre:", datos["nombre"]],
        ["Edad:", datos["edad"]],
        ["Objetivo:", datos["tipo"].capitalize()],
        ["Días seleccionados:", datos["dias_usuario"]],
        ["Días en rutina generada:", datos["dias_rutina"]],
        ["Rutina:", datos["rutina"]["nombre"]],
    ]

    tabla = Table(datos_tabla, colWidths=[150, 350])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#AED6F1")),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))

    elements.append(tabla)
    elements.append(Spacer(1, 20))

    # ---- Descripción ----
    elements.append(Paragraph(f"<b>Descripción:</b> {datos['rutina']['descripcion']}", texto))
    elements.append(Spacer(1, 20))

    # ---- Plan de entrenamiento ----
    elements.append(Paragraph("📅 Plan de entrenamiento:", subtitulo))

    for dia, ejercicios in datos['plan'].items():
        elements.append(Paragraph(f"<b>{dia}</b>", texto))
        for e in ejercicios:
            elements.append(Paragraph(f"• {e}", texto))
        elements.append(Spacer(1, 10))

    # ---- Pie de página ----
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        "⚡ ¡Mantén la constancia y la disciplina! Cada día te acerca más a tu objetivo.",
        ParagraphStyle('Pie', parent=styles['Normal'], alignment=1, textColor=colors.gray)
    ))

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Rutina_{datos['nombre'].replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )


if __name__ == '__main__':
    app.run(debug=True)

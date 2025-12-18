"""
Archivo que conecta las funciones del notebook con Streamlit
NO modifica el notebook original, solo importa sus funciones
"""

import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import pyodbc
from transformers import pipeline
import streamlit as st
from openai import OpenAI
import json

# ====================================
# CONFIGURACIÓN
# ====================================

# Configuración de Tesseract (ajusta la ruta según tu instalación)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Configuración de BD (puedes moverlo a config.py)
DB_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': '192.168.1.3',
    'port': 1433,
    'database': 'documents_database',
    'user': 'bricksbreaker',
    'password': 'puchi15063022'
}


# ====================================
# FUNCIONES DE CONEXIÓN BD
# ====================================

@st.cache_resource
def get_db_connection():
    """
    Crea y retorna una conexión a la BD
    Usa cache para evitar reconexiones
    """
    try:
        connection_str = (
            f"DRIVER={{{DB_CONFIG['driver']}}};"
            f"SERVER={DB_CONFIG['server']},{DB_CONFIG['port']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['user']};"
            f"PWD={DB_CONFIG['password']};"
        )
        connection = pyodbc.connect(connection_str)
        return connection
    except Exception as e:
        st.error(f"Error de conexión a BD: {e}")
        return None


def get_categories_from_db():
    """Obtiene las categorías de la BD"""
    connection = get_db_connection()
    if not connection:
        return []
    
    cursor = connection.cursor()
    cursor.execute("SELECT CategoryName FROM dbo.Categories")
    categories = [row[0] for row in cursor.fetchall()]
    return categories


# ====================================
# FUNCIONES OCR (del notebook)
# ====================================

def extract_text_from_pdf(pdf_path):
    """
    Extrae texto de un PDF usando PyMuPDF
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error extrayendo PDF: {e}")
        return ""


def extract_text_from_image(image_path):
    """
    Extrae texto de una imagen usando Tesseract OCR
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.error(f"Error extrayendo imagen: {e}")
        return ""


# ====================================
# FUNCIONES DE CLASIFICACIÓN IA
# ====================================

@st.cache_resource
def get_image_classifier():
    """
    Carga el modelo de clasificación zero-shot
    Usa cache para evitar recargar el modelo
    """
    try:
        classifier = pipeline(
            "zero-shot-image-classification",
            model="facebook/metaclip-b16-fullcc2.5b"
        )
        return classifier
    except Exception as e:
        st.error(f"Error cargando modelo: {e}")
        return None


def clasificar_imagen_zero_shot(ruta_imagen, etiquetas=None):
    """
    Clasifica una imagen usando zero-shot classification
    """
    if etiquetas is None:
        etiquetas = [
            "Contrato", "Factura", "Recibo", "Identificación personal",
            "Informe", "Currículum / Hoja de vida", "Certificado",
            "Licencia o permiso", "Correspondencia (cartas, emails)",
            "Documentación legal", "Documentación técnica", "Manual o guía",
            "Proyecto", "Planificación / Agenda", "Otros"
        ]
    
    classifier = get_image_classifier()
    if not classifier:
        return None
    
    try:
        imagen = Image.open(ruta_imagen)
        resultado = classifier(imagen, candidate_labels=etiquetas)
        return resultado
    except Exception as e:
        st.error(f"Error clasificando imagen: {e}")
        return None


# ====================================
# BÚSQUEDA INTELIGENTE CON DEEPSEEK
# ====================================

def buscar_documentos_inteligente(consulta_usuario, api_key):
    """
    Sistema de búsqueda inteligente usando Deepseek AI
    """
    categorias = get_categories_from_db()
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )
    
    prompt = f"""
Eres un asistente que ayuda a buscar documentos en una base de datos.

Categorías disponibles: {', '.join(categorias)}

Consulta del usuario: "{consulta_usuario}"

Analiza la consulta y genera parámetros de búsqueda en formato JSON con esta estructura:
{{
    "categoria": "nombre de categoría o null si no se especifica",
    "fecha_desde": "YYYY-MM-DD o null",
    "fecha_hasta": "YYYY-MM-DD o null",
    "palabras_clave": ["palabra1", "palabra2"] o [],
    "extension": ".pdf, .jpg, .png o null",
    "explicacion": "breve explicación de lo que entendiste"
}}

Responde SOLO con el JSON, sin texto adicional.
"""
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en búsqueda de documentos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        respuesta_ia = response.choices[0].message.content
        parametros = json.loads(respuesta_ia)
        
        # Ejecutar búsqueda en BD
        resultados = ejecutar_busqueda_bd(parametros)
        
        return parametros, resultados
        
    except Exception as e:
        st.error(f"Error en búsqueda inteligente: {e}")
        return None, []


def ejecutar_busqueda_bd(parametros):
    """
    Ejecuta la búsqueda en la base de datos según los parámetros
    """
    connection = get_db_connection()
    if not connection:
        return []
    
    cursor = connection.cursor()
    
    query = """
        SELECT 
            d.DocumentID,
            d.FilePath,
            d.Uploaded,
            c.CategoryName,
            d.ExtractedText
        FROM dbo.Documents d
        LEFT JOIN dbo.Categories c ON d.CategoryID = c.CategoryID
        WHERE 1=1
    """
    
    params = []
    
    # Filtros dinámicos
    if parametros.get('categoria'):
        query += " AND c.CategoryName = ?"
        params.append(parametros['categoria'])
    
    if parametros.get('fecha_desde'):
        query += " AND d.Uploaded >= ?"
        params.append(parametros['fecha_desde'])
    
    if parametros.get('fecha_hasta'):
        query += " AND d.Uploaded <= ?"
        params.append(parametros['fecha_hasta'])
    
    if parametros.get('palabras_clave'):
        for palabra in parametros['palabras_clave']:
            query += " AND d.ExtractedText LIKE ?"
            params.append(f"%{palabra}%")
    
    if parametros.get('extension'):
        query += " AND d.FilePath LIKE ?"
        params.append(f"%{parametros['extension']}")
    
    try:
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        
        documentos = []
        for row in resultados:
            documentos.append({
                'DocumentID': row[0],
                'FilePath': row[1],
                'Uploaded': row[2],
                'CategoryName': row[3],
                'ExtractedText': row[4][:200] + "..." if row[4] else ""
            })
        
        return documentos
    except Exception as e:
        st.error(f"Error ejecutando búsqueda: {e}")
        return []


# ====================================
# FUNCIONES DE BD
# ====================================

def insert_document(CategoryID, FilePath, Uploaded, ExtractedText):
    """
    Inserta un documento en la BD
    """
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO dbo.Documents (CategoryID, FilePath, Uploaded, ExtractedText)
            VALUES (?, ?, ?, ?)
        """, (CategoryID, FilePath, Uploaded, ExtractedText))
        connection.commit()
        return True
    except Exception as e:
        st.error(f"Error insertando documento: {e}")
        return False


def get_category_id_by_name(category_name):
    """
    Obtiene el ID de una categoría por nombre
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT CategoryID FROM dbo.Categories WHERE CategoryName = ?", (category_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        st.error(f"Error obteniendo categoría: {e}")
        return None
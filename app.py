import streamlit as st
import sys
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Gestión Documental con IA",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📄 Sistema Inteligente de Gestión Documental")
st.markdown("---")

# Sidebar para navegación
st.sidebar.title("🔍 Navegación")
pagina = st.sidebar.radio(
    "Selecciona una opción:",
    ["🏠 Inicio", "📤 Cargar Documentos", "🔎 Búsqueda Inteligente", "📊 Dashboard", "⚙️ Configuración"]
)

# PÁGINA: INICIO

if pagina == "🏠 Inicio":
    st.header("Bienvenido al Sistema de Gestión Documental")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✨ Características")
        st.markdown("""
        - **OCR Avanzado**: Extracción de texto con Tesseract
        - **Clasificación IA**: Zero-shot classification con Hugging Face
        - **Búsqueda Inteligente**: Consultas en lenguaje natural con Deepseek
        - **Base de Datos**: Almacenamiento en SQL Server
        """)
        
    with col2:
        st.subheader("📈 Estadísticas")
        # Aquí puedes agregar estadísticas reales de tu BD
        st.metric("Documentos Totales", "—", help="Conecta a tu BD para ver stats")
        st.metric("Categorías", "15", help="Categorías predefinidas")
        st.metric("Precisión IA", "60-100%", help="Según tipo de documento")
    
    st.markdown("---")
    st.info("💡 **Tip**: Comienza subiendo un documento en la sección 'Cargar Documentos'")


# PÁGINA: CARGAR DOCUMENTOS

elif pagina == "📤 Cargar Documentos":
    st.header("📤 Cargar y Clasificar Documentos")
    
    # Tabs para diferentes tipos de carga
    tab1, tab2 = st.tabs(["📁 Archivo Individual", "📂 Múltiples Archivos"])
    
    with tab1:
        uploaded_file = st.file_uploader(
            "Selecciona un documento (PDF, JPG, PNG)",
            type=['pdf', 'jpg', 'png', 'jpeg'],
            help="Formatos soportados: PDF, JPG, PNG"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.success(f"✅ Archivo cargado: **{uploaded_file.name}**")
                st.write(f"📊 Tamaño: {uploaded_file.size / 1024:.2f} KB")
                st.write(f"📄 Tipo: {uploaded_file.type}")
            
            with col2:
                if st.button("🚀 Procesar Documento", type="primary"):
                    with st.spinner("🔄 Extrayendo texto..."):
                        # Aquí llamarías a tus funciones del notebook
                        st.write("⚠️ **Nota**: Conecta las funciones del notebook aquí")
                        # Ejemplo:
                        # from doc_finder import extract_text_from_pdf, clasificar_imagen_zero_shot
                        # texto = extract_text_from_pdf(uploaded_file)
                        # resultado = clasificar_imagen_zero_shot(uploaded_file)
                    
                    st.success("✅ Documento procesado exitosamente")
                    
                    # Mostrar resultados simulados
                    with st.expander("📋 Ver texto extraído"):
                        st.text_area("Texto OCR", "Aquí aparecerá el texto extraído...", height=200)
                    
                    with st.expander("🏷️ Clasificación IA"):
                        st.write("**Categoría detectada:** Certificado")
                        st.progress(0.75, text="Confianza: 75%")
    
    with tab2:
        uploaded_files = st.file_uploader(
            "Selecciona múltiples documentos",
            type=['pdf', 'jpg', 'png', 'jpeg'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.write(f"📊 **{len(uploaded_files)} archivos seleccionados**")
            
            for file in uploaded_files:
                st.write(f"- {file.name}")
            
            if st.button("🚀 Procesar Todos", type="primary"):
                progress_bar = st.progress(0)
                for i, file in enumerate(uploaded_files):
                    with st.spinner(f"Procesando {file.name}..."):
                        # Procesar cada archivo
                        progress_bar.progress((i + 1) / len(uploaded_files))
                
                st.success(f"✅ {len(uploaded_files)} documentos procesados")


# PÁGINA: BÚSQUEDA INTELIGENTE

elif pagina == "🔎 Búsqueda Inteligente":
    st.header("🔎 Búsqueda Inteligente con IA")
    
    st.markdown("""
    Realiza búsquedas en lenguaje natural. Ejemplos:
    - *"Busca todo tipo de documentos cargados en esta base de datos"*
    """)
    
    # Input de búsqueda
    consulta = st.text_input(
        "🔍 Escribe tu consulta:",
        placeholder="Ej: Busca todos los certificados del 2025",
        help="Usa lenguaje natural, la IA interpretará tu consulta"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        buscar_btn = st.button("🚀 Buscar", type="primary", use_container_width=True)
    with col2:
        st.button("🔄 Limpiar", use_container_width=True)
    
    if buscar_btn and consulta:
        with st.spinner("🤖 La IA está interpretando tu consulta..."):
            # Aquí llamarías a buscar_documentos_inteligente(consulta)
            st.info(f"🤖 **IA entendió:** Buscar documentos de tipo certificado del año 2025")
        
        st.markdown("---")
        st.subheader("📊 Resultados")
        
        # Resultados simulados
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write("**📄 certificado_onapi.png**")
                st.caption("Extracto: Registro de nombre comercial...")
            
            with col2:
                st.write("📂 Certificado")
                st.write("📅 2025-01-15")
            
            with col3:
                st.button("👁️ Ver", key="ver1")
        
        st.markdown("---")
        
        # Filtros adicionales
        with st.expander("🔧 Filtros Avanzados"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.selectbox("Categoría", ["Todas", "Contrato", "Factura", "Certificado"])
            
            with col2:
                st.date_input("Fecha desde")
            
            with col3:
                st.date_input("Fecha hasta")


# PÁGINA: DASHBOARD

elif pagina == "📊 Dashboard":
    st.header("📊 Dashboard de Documentos")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Total Docs", "—", help="Conecta a tu BD")
    
    with col2:
        st.metric("📤 Subidos Hoy", "—")
    
    with col3:
        st.metric("🎯 Precisión Media", "75%")
    
    with col4:
        st.metric("⚡ Velocidad", "2.3s/doc")
    
    st.markdown("---")
    
    # Gráficos (placeholder)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Documentos por Categoría")
        st.bar_chart({"Certificados": 5, "Contratos": 3, "Facturas": 2})
    
    with col2:
        st.subheader("📅 Documentos por Mes")
        st.line_chart({"Ene": 10, "Feb": 15, "Mar": 12})


# PÁGINA: CONFIGURACIÓN

elif pagina == "⚙️ Configuración":
    st.header("⚙️ Configuración del Sistema")
    
    with st.expander("🗄️ Configuración de Base de Datos"):
        st.text_input("Servidor", placeholder="192.168.1.3")
        st.text_input("Puerto", placeholder="1433")
        st.text_input("Base de Datos", placeholder="documents_database")
        st.text_input("Usuario", placeholder="usuario")
        st.text_input("Contraseña", type="password")
        st.button("🔌 Probar Conexión")
    
    with st.expander("🤖 Configuración de IA"):
        st.text_input("Deepseek API Key", type="password", help="Tu API key de Deepseek")
        st.selectbox("Modelo OCR", ["Tesseract", "Google Cloud Vision", "AWS Textract"])
        st.selectbox("Modelo Clasificación", ["metaclip-b16-fullcc2.5b", "CLIP", "BERT"])
    
    with st.expander("📁 Rutas de Archivos"):
        st.text_input("Carpeta de Documentos", placeholder="C:/Users/Documents")
        st.text_input("Carpeta de Temporales", placeholder="C:/Temp")
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.button("💾 Guardar Cambios", type="primary")
    with col2:
        st.button("🔄 Restaurar Valores por Defecto")


# Footer
st.markdown("---")
st.caption("🔬 Sistema Inteligente de Gestión Documental | Proyecto Universitario INTEC 2025")
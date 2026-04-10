# 🛏️ Sistema de Comisiones - Blancos Primavera

Aplicación Streamlit para gestionar y registrar comisiones de ventas de artículos del catálogo de Blancos Primavera.

## Features

- ✅ **Registrar Ventas**: Ingresa nuevas ventas con vendedor, artículo, cantidad y precio
- 💰 **Cálculo Automático de Comisiones**: Soporta comisiones por porcentaje o monto fijo
- 📊 **Dashboard de Resumen**: Visualiza comisiones por vendedor y totales del día
- 📄 **Generación de PDF**: Crea reportes listos para imprimir
- ✏️ **Edición de Registros**: Modifica o elimina ventas registradas
- ⚙️ **Gestión de Catálogo**: Agrega o edita artículos y sus comisiones

## Instalación Local

1. **Clonar el repositorio**
```bash
git clone https://github.com/tuusuario/app-comisiones.git
cd app-comisiones
```

2. **Crear ambiente virtual (opcional)**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la app**
```bash
streamlit run app.py
```

La app abrirá en `http://localhost:8501`

## Despliegue en Streamlit Cloud

1. Asegúrate de que el repositorio esté en GitHub (público o privado)
2. Ve a https://share.streamlit.io/
3. Haz clic en "New app"
4. Selecciona tu repositorio y rama
5. Especifica el archivo principal: `app.py`
6. ¡Listo! Tu app estará en vivo

## Archivos

- `app.py` - Aplicación principal
- `requirements.txt` - Dependencias de Python
- `catalogo_articulos.csv` - Catálogo de artículos con comisiones (se crea automáticamente)
- `ventas_comisiones.csv` - Registro de ventas (se crea automáticamente)

## Vendedores

- PACO
- YAEL
- ARELY
- DANIEL
- FERNANDO
- ISABELA
- RENATA
- AMEYALI
- PATRICIA SOTO

## Tecnologías

- **Streamlit** - Framework web
- **Pandas** - Manejo de datos
- **FPDF** - Generación de PDFs

---

Desarrollado para Blancos Primavera ❤️

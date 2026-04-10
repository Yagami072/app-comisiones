import streamlit as st
import pandas as pd
from datetime import date
import os
from fpdf import FPDF

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Comisiones Blancos Primavera", layout="wide", page_icon="🛏️")
st.title("🛏️ Sistema de Comisiones - Blancos Primavera")

# --- INICIALIZACIÓN DE DATOS ---
VENDEDORES = ["PACO", "YAEL", "ARELY", "DANIEL", "FERNANDO", "ISABELA", "RENATA", "AMEYALI", "PATRICIA SOTO"]

# Si no existe el catálogo de artículos, lo creamos con tus datos iniciales
if not os.path.exists("catalogo_articulos.csv"):
    articulos_3 = ["Frazada Peluda", "Cortina Bordada Cruzada", "Cortina Bordada Doble", "Cortina Bordada", "Michi Abrazable", "Borrega Generico Mat", "Borrega Generico Ks", "Borrega Amigo Disney Mat", "Borrega Amigo Disney Ind", "Frazada Voga Casa Isla", "Sabanas Franela Sta Ana", "Cobertor Rashel Mat Generico", "Cobertor Rabbit Colap", "Cola De Sirena", "Cobertor Bonded K.S", "Cobertor Pachonato Mat Ponchito", "Sabanas Franela Disney Ind Colpa", "Bata De Descanso Infantil Licona"]
    articulos_7 = ["Borrega Primavera Jumbo", "Borrega Primavera K.S", "Cobertor ligero Luxus", "Cobertor ligero Borrega", "Cobertor ligero Con Mangas", "Chal", "Esquimo", "Bata De Descanso", "Sabanas Invernal", "Bata Descanso Borrega"]
    
    data = [{"Artículo": art, "Porcentaje": 0.03} for art in articulos_3] + [{"Artículo": art, "Porcentaje": 0.07} for art in articulos_7]
    pd.DataFrame(data).to_csv("catalogo_articulos.csv", index=False)

# Si no existe el registro de ventas, lo creamos vacío
if not os.path.exists("ventas_comisiones.csv"):
    df_vacia = pd.DataFrame(columns=["ID", "Fecha", "Vendedor", "Artículo", "Precio", "Porcentaje", "Comision"])
    df_vacia.to_csv("ventas_comisiones.csv", index=False)

# Cargar los datos
df_catalogo = pd.read_csv("catalogo_articulos.csv")
df_ventas = pd.read_csv("ventas_comisiones.csv")

# --- NAVEGACIÓN CON PESTAÑAS (TABS) ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 Registrar Venta", "📊 Resumen y PDF", "✏️ Editar Registros", "⚙️ Catálogo de Artículos"])

# --- PESTAÑA 1: REGISTRAR VENTA ---
with tab1:
    st.header("Nueva Venta")
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("Fecha de venta", date.today())
        vendedor = st.selectbox("Compañero", VENDEDORES)
    with col2:
        articulo = st.selectbox("Artículo vendido", df_catalogo["Artículo"].tolist())
        precio = st.number_input("Precio de venta ($)", min_value=0.0, step=50.0)
        
    if st.button("Registrar Venta", type="primary"):
        if precio > 0:
            porcentaje = df_catalogo.loc[df_catalogo["Artículo"] == articulo, "Porcentaje"].values[0]
            comision = precio * porcentaje
            nuevo_id = len(df_ventas) + 1
            
            nueva_venta = pd.DataFrame([{
                "ID": nuevo_id, "Fecha": str(fecha), "Vendedor": vendedor, 
                "Artículo": articulo, "Precio": precio, "Porcentaje": porcentaje, "Comision": comision
            }])
            
            df_ventas = pd.concat([df_ventas, nueva_venta], ignore_index=True)
            df_ventas.to_csv("ventas_comisiones.csv", index=False)
            st.success(f"✅ Venta registrada: {vendedor} ganó ${comision:.2f} de comisión.")
        else:
            st.error("El precio debe ser mayor a 0.")

# --- PESTAÑA 2: RESUMEN Y PDF ---
with tab2:
    st.header("Resumen de Comisiones")
    fecha_filtro = st.date_input("Filtrar por fecha", date.today(), key="filtro_fecha")
    
    df_filtrado = df_ventas[df_ventas["Fecha"] == str(fecha_filtro)]
    
    if not df_filtrado.empty:
        # Mostrar resumen agrupado
        resumen = df_filtrado.groupby("Vendedor")["Comision"].sum().reset_index()
        resumen.columns = ["Vendedor", "Total a Pagar ($)"]
        st.dataframe(resumen, use_container_width=True, hide_index=True)
        
        # Generar PDF
        if st.button("📄 Generar PDF del Día"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt=f"REPORTE DE COMISIONES - BLANCOS PRIMAVERA", ln=True, align='C')
            pdf.set_font("Arial", '', 12)
            pdf.cell(200, 10, txt=f"Fecha: {fecha_filtro}", ln=True, align='C')
            pdf.ln(10)
            
            for vend in df_filtrado["Vendedor"].unique():
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(200, 10, txt=f"VENDEDOR: {vend}", ln=True)
                pdf.set_font("Arial", '', 10)
                
                ventas_vend = df_filtrado[df_filtrado["Vendedor"] == vend]
                total_vend = 0
                for _, row in ventas_vend.iterrows():
                    texto_venta = f"- {row['Artículo']} | Precio: ${row['Precio']:.2f} | Comision: ${row['Comision']:.2f}"
                    pdf.cell(200, 8, txt=texto_venta, ln=True)
                    total_vend += row['Comision']
                
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(200, 8, txt=f"TOTAL A PAGAR: ${total_vend:.2f}", ln=True)
                pdf.ln(5)
            
            pdf.output("Reporte_Comisiones.pdf")
            with open("Reporte_Comisiones.pdf", "rb") as file:
                st.download_button(label="⬇️ Descargar PDF", data=file, file_name=f"Comisiones_{fecha_filtro}.pdf", mime="application/pdf")
    else:
        st.info("No hay ventas registradas en esta fecha.")

# --- PESTAÑA 3: EDITAR REGISTROS (CORREGIR ERRORES) ---
with tab3:
    st.header("Modificar o Borrar Ventas")
    st.write("Si te equivocaste, corrige los datos en la tabla. Los cambios se guardarán solos. Recuerda que si cambias el precio o porcentaje, debes calcular la comisión manualmente por ahora.")
    df_ventas_editado = st.data_editor(df_ventas, num_rows="dynamic", use_container_width=True, key="editor_ventas")
    
    if st.button("Guardar Cambios en Registros"):
        df_ventas_editado.to_csv("ventas_comisiones.csv", index=False)
        st.success("Cambios guardados correctamente.")

# --- PESTAÑA 4: CATÁLOGO DE ARTÍCULOS ---
with tab4:
    st.header("Agregar o Editar Artículos a Comisión")
    st.write("Agrega nuevos artículos al final de la tabla o modifica los porcentajes (ej. 0.03 para 3%, 0.07 para 7%).")
    df_catalogo_editado = st.data_editor(df_catalogo, num_rows="dynamic", use_container_width=True, key="editor_catalogo")
    
    if st.button("Guardar Cambios en Catálogo"):
        df_catalogo_editado.to_csv("catalogo_articulos.csv", index=False)
        st.success("Catálogo actualizado. Los nuevos artículos ya aparecen en el formulario.")
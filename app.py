import streamlit as st
import pandas as pd
from datetime import date
import os
from fpdf import FPDF

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Comisiones Blancos Primavera", layout="wide", page_icon="🛏️")
st.title("🛏️ Sistema de Comisiones - Blancos Primavera")

# --- MIGRACIÓN AUTOMÁTICA DE DATOS ---
if os.path.exists("catalogo_articulos.csv"):
    df_cat_temp = pd.read_csv("catalogo_articulos.csv")
    if "Porcentaje" in df_cat_temp.columns and "Tipo" not in df_cat_temp.columns:
        df_cat_temp["Tipo"] = "Porcentaje"
        df_cat_temp["Valor"] = df_cat_temp["Porcentaje"]
        df_cat_temp = df_cat_temp.drop(columns=["Porcentaje"])
        df_cat_temp.to_csv("catalogo_articulos.csv", index=False)

if os.path.exists("ventas_comisiones.csv"):
    df_ven_temp = pd.read_csv("ventas_comisiones.csv")
    if "Porcentaje" in df_ven_temp.columns and "Tipo Comision" not in df_ven_temp.columns:
        df_ven_temp["Tipo Comision"] = "Porcentaje"
        df_ven_temp["Valor Aplicado"] = df_ven_temp["Porcentaje"]
        df_ven_temp = df_ven_temp.drop(columns=["Porcentaje"])
        df_ven_temp.to_csv("ventas_comisiones.csv", index=False)

# --- INICIALIZACIÓN DE DATOS ---
VENDEDORES = ["PACO", "YAEL", "ARELY", "DANIEL", "FERNANDO", "ISABELA", "RENATA", "AMEYALI", "PATRICIA SOTO"]

if not os.path.exists("catalogo_articulos.csv"):
    articulos_3 = ["Frazada Peluda", "Cortina Bordada Cruzada", "Cortina Bordada Doble", "Cortina Bordada", "Michi Abrazable", "Borrega Generico Mat", "Borrega Generico Ks", "Borrega Amigo Disney Mat", "Borrega Amigo Disney Ind", "Frazada Voga Casa Isla", "Sabanas Franela Sta Ana", "Cobertor Rashel Mat Generico", "Cobertor Rabbit Colap", "Cola De Sirena", "Cobertor Bonded K.S", "Cobertor Pachonato Mat Ponchito", "Sabanas Franela Disney Ind Colpa", "Bata De Descanso Infantil Licona"]
    articulos_7 = ["Borrega Primavera Jumbo", "Borrega Primavera K.S", "Cobertor ligero Luxus", "Cobertor ligero Borrega", "Cobertor ligero Con Mangas", "Chal", "Esquimo", "Bata De Descanso", "Sabanas Invernal", "Bata Descanso Borrega"]
    
    data = [{"Artículo": art, "Tipo": "Porcentaje", "Valor": 0.03} for art in articulos_3] + [{"Artículo": art, "Tipo": "Porcentaje", "Valor": 0.07} for art in articulos_7]
    pd.DataFrame(data).to_csv("catalogo_articulos.csv", index=False)

if not os.path.exists("ventas_comisiones.csv"):
    df_vacia = pd.DataFrame(columns=["ID", "Fecha", "Vendedor", "Artículo", "Cantidad", "Precio Unitario", "Precio Total", "Tipo Comision", "Valor Aplicado", "Comision"])
    df_vacia.to_csv("ventas_comisiones.csv", index=False)

# Cargar los datos ya actualizados
df_catalogo = pd.read_csv("catalogo_articulos.csv")
df_ventas = pd.read_csv("ventas_comisiones.csv")

# --- NAVEGACIÓN ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 Registrar Venta", "📊 Resumen y PDF", "✏️ Editar Registros", "⚙️ Catálogo de Artículos"])

# --- PESTAÑA 1: REGISTRAR VENTA ---
with tab1:
    st.header("Nueva Venta")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        fecha = st.date_input("Fecha de venta", date.today())
        vendedor = st.selectbox("Compañero", VENDEDORES)
        articulo = st.selectbox("Artículo vendido", df_catalogo["Artículo"].tolist())
    with col2:
        precio_unitario = st.number_input("Precio Unitario ($)", min_value=0.0, step=50.0)
        cantidad = st.number_input("Cantidad de piezas", min_value=1, step=1, value=1)
    
    with col3:
        st.info(f"**Total Venta:**\n${precio_unitario * cantidad:,.2f}")
        
    if st.button("Registrar Venta", type="primary", use_container_width=True):
        # AHORA PERMITE VALORES EN 0
        if precio_unitario >= 0:
            tipo_comision = df_catalogo.loc[df_catalogo["Artículo"] == articulo, "Tipo"].values[0]
            valor_aplicado = float(df_catalogo.loc[df_catalogo["Artículo"] == articulo, "Valor"].values[0])
            precio_total = precio_unitario * cantidad
            
            if tipo_comision == "Porcentaje":
                comision = precio_total * valor_aplicado
            elif tipo_comision == "Monto Fijo":
                comision = valor_aplicado * cantidad
            
            nuevo_id = len(df_ventas) + 1
            
            nueva_venta = pd.DataFrame([{
                "ID": nuevo_id, "Fecha": str(fecha), "Vendedor": vendedor, 
                "Artículo": articulo, "Cantidad": cantidad, "Precio Unitario": precio_unitario,
                "Precio Total": precio_total, "Tipo Comision": tipo_comision, 
                "Valor Aplicado": valor_aplicado, "Comision": comision
            }])
            
            df_ventas = pd.concat([df_ventas, nueva_venta], ignore_index=True)
            df_ventas.to_csv("ventas_comisiones.csv", index=False)
            
            st.success(f"✅ ¡Venta registrada exitosamente! \n\n**{cantidad}x {articulo}**. \nComisión asegurada para **{vendedor}**: ${comision:.2f}")
            st.toast(f"✅ Venta de {vendedor} guardada", icon="🎉")
        else:
            st.error("El precio no puede ser negativo.")

# --- PESTAÑA 2: RESUMEN Y PDF ---
with tab2:
    st.header("Dashboard de Comisiones")
    fecha_filtro = st.date_input("Filtrar por fecha", date.today(), key="filtro_fecha")
    df_filtrado = df_ventas[df_ventas["Fecha"] == str(fecha_filtro)]
    
    if not df_filtrado.empty:
        gran_total = df_filtrado["Comision"].sum()
        total_ventas_dinero = df_filtrado["Precio Total"].sum()
        articulos_vendidos = df_filtrado["Cantidad"].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Total a Repartir", f"${gran_total:,.2f}")
        m2.metric("📦 Artículos Vendidos", f"{articulos_vendidos} pzas")
        m3.metric("💵 Ingreso Total en Caja", f"${total_ventas_dinero:,.2f}")
        
        st.markdown("---")
        st.subheader("Desglose por Vendedor")
        
        resumen = df_filtrado.groupby("Vendedor")["Comision"].sum().reset_index()
        resumen = resumen.sort_values(by="Comision", ascending=False)
        st.bar_chart(resumen.set_index("Vendedor"))
        
        st.markdown("---")
        
        if st.button("📄 Generar PDF del Día", type="primary"):
            pdf = FPDF()
            pdf.add_page()
            
            pdf.set_font("Arial", 'B', 16)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 10, txt="REPORTE DE COMISIONES - BLANCOS PRIMAVERA", ln=True, align='C')
            pdf.set_font("Arial", '', 12)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 10, txt=f"Fecha de corte: {fecha_filtro}", ln=True, align='C')
            pdf.ln(5)
            
            for vend in df_filtrado["Vendedor"].unique():
                pdf.set_font("Arial", 'B', 12)
                pdf.set_fill_color(220, 235, 255)
                pdf.cell(0, 10, txt=f"  VENDEDOR: {vend}", ln=True, fill=True)
                
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(15, 8, "Cant.", border=1, align='C')
                pdf.cell(105, 8, "Articulo", border=1)
                pdf.cell(35, 8, "Venta", border=1, align='C')
                pdf.cell(35, 8, "Comision", border=1, align='C', ln=True)
                
                pdf.set_font("Arial", '', 10)
                ventas_vend = df_filtrado[df_filtrado["Vendedor"] == vend]
                total_vend = 0
                for _, row in ventas_vend.iterrows():
                    pdf.cell(15, 8, str(row['Cantidad']), border=1, align='C')
                    pdf.cell(105, 8, str(row['Artículo'])[:48], border=1)
                    pdf.cell(35, 8, f"${row['Precio Total']:,.2f}", border=1, align='R')
                    pdf.cell(35, 8, f"${row['Comision']:,.2f}", border=1, align='R', ln=True)
                    total_vend += row['Comision']
                
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(155, 8, "TOTAL A PAGAR AL VENDEDOR:", border=1, align='R')
                pdf.set_fill_color(200, 255, 200)
                pdf.cell(35, 8, f"${total_vend:,.2f}", border=1, align='R', ln=True, fill=True)
                pdf.ln(8)
            
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 14)
            pdf.set_fill_color(255, 220, 220)
            pdf.cell(0, 12, txt=f"GRAN TOTAL A REPARTIR HOY: ${gran_total:,.2f}", ln=True, align='C', fill=True)
            
            pdf.output("Reporte_Comisiones.pdf")
            with open("Reporte_Comisiones.pdf", "rb") as file:
                st.download_button(label="⬇️ Descargar PDF Listo para Imprimir", data=file, file_name=f"Comisiones_{fecha_filtro}.pdf", mime="application/pdf")
    else:
        st.info("No hay ventas registradas en esta fecha.")

# --- PESTAÑA 3: EDITAR REGISTROS ---
with tab3:
    st.header("Modificar o Borrar Ventas")
    
    df_ventas_editado = st.data_editor(df_ventas, num_rows="dynamic", use_container_width=True, key="editor_ventas")
    
    if not df_ventas.equals(df_ventas_editado):
        df_ventas_editado.to_csv("ventas_comisiones.csv", index=False)
        st.toast("💾 Registro actualizado. Limpiando memoria...")
        st.rerun() 

# --- PESTAÑA 4: CATÁLOGO DE ARTÍCULOS ---
with tab4:
    st.header("Agregar o Editar Artículos a Comisión")
    st.write("Selecciona si la comisión es por **Porcentaje** o un **Monto Fijo** en pesos directos.")
    
    df_catalogo_editado = st.data_editor(
        df_catalogo, 
        num_rows="dynamic", 
        use_container_width=True, 
        key="editor_catalogo",
        column_config={
            "Tipo": st.column_config.SelectboxColumn(
                "Tipo de Comisión",
                help="Elige si se calcula como porcentaje o monto directo",
                options=["Porcentaje", "Monto Fijo"],
                required=True
            ),
            "Valor": st.column_config.NumberColumn(
                "Valor de Comisión",
                help="Ejemplo: 0.03 (para 3%) o 50.0 (para $50 pesos por pieza)",
                required=True
            )
        }
    )
    
    if not df_catalogo.equals(df_catalogo_editado):
        df_catalogo_editado.to_csv("catalogo_articulos.csv", index=False)
        st.toast("💾 Catálogo actualizado.")
        st.rerun()
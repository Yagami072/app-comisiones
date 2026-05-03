import streamlit as st
import pandas as pd
from datetime import date
import os
from fpdf import FPDF
import time
from io import BytesIO

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
    precio_key = "precio_unitario_input"
    reset_key = "precio_unitario_reset"
    cantidad_key = "cantidad_piezas_input"
    cantidad_reset_key = "cantidad_piezas_reset"
    success_msg_key = "venta_guardada_msg"
    success_toast_key = "venta_guardada_toast"
    articulo_key = "articulo_input"
    articulo_reset_key = "articulo_reset"
    articulo_init_key = "articulo_init_done"
    porcentaje_custom_key = "porcentaje_custom"
    porcentaje_custom_val_key = "porcentaje_custom_val"
    porcentaje_custom_reset_key = "porcentaje_custom_reset"
    cooldown_key = "registro_cooldown_until"
    cooldown_seconds = 3
    fecha_confirmada_key = "fecha_confirmada"
    fecha_input_key = "fecha_input"
    fecha_editing_key = "fecha_editing"
    fecha_input_reset_key = "fecha_input_reset"
    fecha_editing_reset_key = "fecha_editing_reset"

    if reset_key not in st.session_state:
        st.session_state[reset_key] = False
    if cantidad_reset_key not in st.session_state:
        st.session_state[cantidad_reset_key] = False
    if cantidad_key not in st.session_state:
        st.session_state[cantidad_key] = 1

    if st.session_state[reset_key]:
        st.session_state[precio_key] = 0.0
        st.session_state[reset_key] = False
    if st.session_state[cantidad_reset_key]:
        st.session_state[cantidad_key] = 1
        st.session_state[cantidad_reset_key] = False

    if success_msg_key in st.session_state:
        st.success(st.session_state.pop(success_msg_key))
        toast_msg = st.session_state.pop(success_toast_key, None)
        if toast_msg:
            st.toast(toast_msg, icon="🎉")

    if articulo_reset_key not in st.session_state:
        st.session_state[articulo_reset_key] = False
    if st.session_state[articulo_reset_key]:
        st.session_state[articulo_key] = None
        st.session_state[articulo_reset_key] = False
    if articulo_init_key not in st.session_state:
        st.session_state[articulo_key] = None
        st.session_state[articulo_init_key] = True
    if porcentaje_custom_reset_key in st.session_state and st.session_state[porcentaje_custom_reset_key]:
        st.session_state[porcentaje_custom_key] = False
        st.session_state[porcentaje_custom_val_key] = 0.0
        st.session_state[porcentaje_custom_reset_key] = False
    if cooldown_key not in st.session_state:
        st.session_state[cooldown_key] = 0.0

    if fecha_confirmada_key not in st.session_state:
        st.session_state[fecha_confirmada_key] = date.today()
    if fecha_input_key not in st.session_state:
        st.session_state[fecha_input_key] = st.session_state[fecha_confirmada_key]
    if fecha_editing_key not in st.session_state:
        st.session_state[fecha_editing_key] = False
    if fecha_input_reset_key not in st.session_state:
        st.session_state[fecha_input_reset_key] = False
    if fecha_editing_reset_key not in st.session_state:
        st.session_state[fecha_editing_reset_key] = False

    if st.session_state[fecha_input_reset_key]:
        st.session_state[fecha_input_key] = st.session_state[fecha_confirmada_key]
        st.session_state[fecha_input_reset_key] = False
    if st.session_state[fecha_editing_reset_key]:
        st.session_state[fecha_editing_key] = False
        st.session_state[fecha_editing_reset_key] = False
    
    with col1:
        editar_fecha = st.checkbox("Modificar fecha", key=fecha_editing_key)
        fecha_seleccionada = st.date_input("Fecha de venta", key=fecha_input_key, disabled=not editar_fecha)
        vendedor = st.selectbox("Compañero", VENDEDORES)
        articulo = st.selectbox(
            "Artículo vendido",
            df_catalogo["Artículo"].tolist(),
            key=articulo_key,
            index=None,
            placeholder="Busca un articulo..."
        )
    with col2:
        precio_unitario = st.number_input("Precio Unitario ($)", min_value=0.0, step=50.0, key=precio_key)
        cantidad = st.number_input("Cantidad de piezas", min_value=1, step=1, key=cantidad_key)
        usar_porcentaje_personalizado = st.checkbox("Usar porcentaje personalizado", key=porcentaje_custom_key)
        porcentaje_personalizado = None
        if usar_porcentaje_personalizado:
            porcentaje_personalizado = st.number_input(
                "Porcentaje personalizado (%)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Acepta 7 o 0.07",
                key=porcentaje_custom_val_key
            )
    
    with col3:
        st.info(f"**Total Venta:**\n${precio_unitario * cantidad:,.2f}")

    if editar_fecha and fecha_seleccionada != st.session_state[fecha_confirmada_key]:
        st.warning("La fecha cambio. Confirma para continuar.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Confirmar fecha"):
                st.session_state[fecha_confirmada_key] = fecha_seleccionada
                st.session_state[fecha_input_reset_key] = True
                st.session_state[fecha_editing_reset_key] = True
                st.toast("Fecha confirmada.")
                st.rerun()
        with c2:
            if st.button("Cancelar cambio"):
                st.session_state[fecha_input_reset_key] = True
                st.session_state[fecha_editing_reset_key] = True
                st.toast("Cambio de fecha cancelado.")
                st.rerun()

    if not editar_fecha and fecha_seleccionada != st.session_state[fecha_confirmada_key]:
        st.session_state[fecha_input_reset_key] = True
        st.rerun()
        
    cooldown_remaining = max(0.0, st.session_state[cooldown_key] - time.time())
    if cooldown_remaining > 0:
        st.caption(f"Espera {int(cooldown_remaining) + 1}s para registrar otra venta.")
        time.sleep(min(1.0, cooldown_remaining))
        st.rerun()

    if st.button(
        "Registrar Venta",
        type="primary",
        use_container_width=True,
        disabled=cooldown_remaining > 0
    ):
        puede_guardar = True
        if fecha_seleccionada != st.session_state[fecha_confirmada_key]:
            st.error("Confirma la fecha antes de registrar la venta.")
            puede_guardar = False
        elif not articulo:
            st.error("Selecciona un artículo para registrar la venta.")
            puede_guardar = False
        elif precio_unitario <= 0:
            st.error("No se puede guardar la venta hasta que se ingrese el costo.")
            puede_guardar = False
        else:
            if usar_porcentaje_personalizado:
                porcentaje_custom = (
                    porcentaje_personalizado / 100
                    if porcentaje_personalizado and porcentaje_personalizado > 1
                    else (porcentaje_personalizado or 0.0)
                )
                if porcentaje_custom <= 0:
                    st.error("Ingresa un porcentaje válido para registrar la venta.")
                    puede_guardar = False
                else:
                    tipo_comision = "Porcentaje"
                    valor_aplicado = porcentaje_custom
                    precio_total = precio_unitario * cantidad
                    comision = precio_total * valor_aplicado
            else:
                tipo_comision = df_catalogo.loc[df_catalogo["Artículo"] == articulo, "Tipo"].values[0]
                valor_aplicado = float(df_catalogo.loc[df_catalogo["Artículo"] == articulo, "Valor"].values[0])
                precio_total = precio_unitario * cantidad
                
                if tipo_comision == "Porcentaje":
                    comision = precio_total * valor_aplicado
                elif tipo_comision == "Monto Fijo":
                    comision = valor_aplicado * cantidad

        if puede_guardar:
            nuevo_id = len(df_ventas) + 1
            
            nueva_venta = pd.DataFrame([{
                "ID": nuevo_id, "Fecha": str(st.session_state[fecha_confirmada_key]), "Vendedor": vendedor, 
                "Artículo": articulo, "Cantidad": cantidad, "Precio Unitario": precio_unitario,
                "Precio Total": precio_total, "Tipo Comision": tipo_comision, 
                "Valor Aplicado": valor_aplicado, "Comision": comision
            }])
            
            df_ventas = pd.concat([df_ventas, nueva_venta], ignore_index=True)
            df_ventas.to_csv("ventas_comisiones.csv", index=False)
            
            st.session_state[success_msg_key] = (
                f"✅ ¡Venta registrada exitosamente! \n\n**{cantidad}x {articulo}**. "
                f"\nComisión asegurada para **{vendedor}**: ${comision:.2f}"
            )
            st.session_state[success_toast_key] = f"✅ Venta de {vendedor} guardada"
            st.session_state[reset_key] = True
            st.session_state[articulo_reset_key] = True
            st.session_state[porcentaje_custom_reset_key] = True
            st.session_state[cantidad_reset_key] = True
            st.session_state[cooldown_key] = time.time() + cooldown_seconds
            st.rerun()

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

        excel_df = df_filtrado.copy()
        percent_cols = {"Porcentaje", "Valor Aplicado"}
        for col in percent_cols:
            if col in excel_df.columns:
                col_num = pd.to_numeric(excel_df[col], errors="coerce")
                excel_df[col] = col_num.where(col_num <= 1, col_num / 100)
        if "Precio" in excel_df.columns:
            excel_df = excel_df.drop(columns=["Precio"])
        desired_order = [
            "ID",
            "Fecha",
            "Vendedor",
            "Artículo",
            "Cantidad",
            "Precio Unitario",
            "Precio Total",
            "Tipo Comision",
            "Valor Aplicado",
            "Porcentaje",
            "Comision"
        ]
        ordered_cols = [c for c in desired_order if c in excel_df.columns]
        ordered_cols += [c for c in excel_df.columns if c not in desired_order]
        excel_df = excel_df[ordered_cols]
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            workbook = writer.book
            sheet_name = "Comisiones"
            start_row = 1
            start_col = 1

            excel_df.to_excel(
                writer,
                index=False,
                sheet_name=sheet_name,
                startrow=start_row,
                startcol=start_col
            )
            ws = writer.sheets[sheet_name]

            title_format = workbook.add_format({
                "bold": True,
                "font_size": 14,
                "align": "left",
                "valign": "vcenter"
            })
            header_format = workbook.add_format({
                "bold": True,
                "bg_color": "#1F4E78",
                "font_color": "#FFFFFF",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True
            })
            base_format = workbook.add_format({"align": "center", "valign": "vcenter"})
            money_format = workbook.add_format({
                "num_format": "$#,##0.00",
                "align": "center",
                "valign": "vcenter"
            })
            percent_format = workbook.add_format({
                "num_format": "0.##%",
                "align": "center",
                "valign": "vcenter"
            })
            date_format = workbook.add_format({
                "num_format": "yyyy-mm-dd",
                "align": "center",
                "valign": "vcenter"
            })
            alt_row_format = workbook.add_format({"bg_color": "#F4F6F8"})

            last_col = start_col + len(excel_df.columns) - 1
            ws.merge_range(0, 0, 0, last_col, f"Comisiones del dia - {fecha_filtro}", title_format)
            ws.set_row(0, 22)

            header_row = start_row
            ws.write(header_row, 0, "Revisado", header_format)
            ws.set_row(header_row, 20, header_format)

            data_start = header_row + 1
            data_end = data_start + len(excel_df) - 1
            for row in range(data_start, data_end + 1):
                ws.write_boolean(row, 0, False)
                ws.insert_checkbox(row, 0, {"cell": f"A{row + 1}", "checked": False})

            ws.set_column(0, 0, 12, base_format)
            ws.freeze_panes(data_start, 1)
            if len(excel_df) > 0:
                filter_first_col = start_col + 1
                filter_last_col = last_col - 1 if "Comision" in excel_df.columns else last_col
                if filter_first_col <= filter_last_col:
                    ws.autofilter(header_row, filter_first_col, header_row, filter_last_col)
                ws.conditional_format(
                    data_start,
                    0,
                    data_end,
                    last_col,
                    {"type": "formula", "criteria": "=MOD(ROW(),2)=0", "format": alt_row_format}
                )

            money_cols = {"Precio", "Precio Unitario", "Precio Total", "Comision"}
            percent_cols = {"Porcentaje", "Valor Aplicado"}
            date_cols = {"Fecha"}
            for idx, col in enumerate(excel_df.columns):
                col_idx = start_col + idx
                if len(excel_df) > 0:
                    col_values = excel_df[col].astype("string").fillna("")
                    max_len_value = col_values.str.len().max()
                    max_len = max(len(col), int(max_len_value) if pd.notna(max_len_value) else 0)
                else:
                    max_len = len(col)
                width = min(max_len + 4, 48)
                fmt = None
                if col in money_cols:
                    fmt = money_format
                elif col in percent_cols:
                    fmt = percent_format
                elif col in date_cols:
                    fmt = date_format
                ws.set_column(col_idx, col_idx, width, fmt or base_format)
        output.seek(0)

        st.download_button(
            label="⬇️ Descargar Excel del Día",
            data=output,
            file_name=f"Comisiones_{fecha_filtro}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
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
    password_key = "catalogo_password"
    autorizado_key = "catalogo_autorizado"
    password_input = st.text_input("Contraseña", type="password", key=password_key)
    if password_input == "Primavera2026":
        st.session_state[autorizado_key] = True
    autorizado = st.session_state.get(autorizado_key, False)
    if not autorizado:
        if password_input:
            st.error("Contraseña incorrecta.")
        st.info("Ingresa la contraseña para editar el catálogo.")
    
    df_catalogo_editado = st.data_editor(
        df_catalogo, 
        num_rows="dynamic", 
        use_container_width=True, 
        key="editor_catalogo",
        disabled=not autorizado,
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
    
    if autorizado and not df_catalogo.equals(df_catalogo_editado):
        df_catalogo_editado.to_csv("catalogo_articulos.csv", index=False)
        st.toast("💾 Catálogo actualizado.")
        st.rerun()
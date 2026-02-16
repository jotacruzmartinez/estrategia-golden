import streamlit as st
import pandas as pd
import pickle
import os
from pesos import extraer_todo_el_mercado
from IA import entrenar_modelo

# CONFIGURACIÓN
ruta_excel = 'HISTORIAL_DIARIO_COMPLETO.xlsx'
ruta_modelo = 'modelo_ia.pkl'
ruta_salida = 'TOP_10_PREDICCIONES.xlsx'

def generar_predicciones():
    if not os.path.exists(ruta_modelo):
        st.error("❌ El modelo no existe.")
        return

    df = pd.read_excel(ruta_excel)
    with open(ruta_modelo, 'rb') as f:
        modelo = pickle.load(f)

    # Lógica de indicadores intacta
    df['Distancia_MA50'] = df['Close'] / df['MA50']
    df['Distancia_MA200'] = df['Close'] / df['MA200']
    df['Volatilidad_Relativa'] = df['ATR'] / df['Close']
    
    ultima_data = df.sort_values('Date').groupby('Ticker').last().reset_index()
    columnas_ia = ['RSI', 'Distancia_MA50', 'Distancia_MA200', 'Volatilidad_Relativa']
    
    X_pred = ultima_data[columnas_ia].fillna(0)
    probs = modelo.predict_proba(X_pred)[:, 1]
    
    # --- CÁLCULOS Y REDONDEOS ---
    ultima_data['Confianza_%'] = (probs * 100).round(2)
    ultima_data['Precio'] = ultima_data['Close'].round(2)
    ultima_data['RSI'] = ultima_data['RSI'].round(2)
    ultima_data['ATR'] = ultima_data['ATR'].round(2)
    
    # 1. STOP LOSS: Basado en 2.0 * ATR
    ultima_data['STOP LOSS'] = (ultima_data['Close'] - (ultima_data['ATR'] * 2)).round(2)
    
    # 2. TAKE PROFITS DINÁMICOS
    # Objetivo 1: Para asegurar ganancias rápido
    ultima_data['TP_CONSERVADOR'] = (ultima_data['Close'] + (ultima_data['ATR'] * 3)).round(2)
    
    # Objetivo 2: Para capturar la tendencia fuerte
    ultima_data['TP_OPTIMISTA'] = (ultima_data['Close'] + (ultima_data['ATR'] * 5)).round(2)

    # Filtro y Orden por Confianza de la IA
    listado_completo = ultima_data[ultima_data['Volume'] > 10].sort_values('Confianza_%', ascending=False)
    
    listado_completo.to_excel(ruta_salida, index=False)
    return listado_completo

# --- INTERFAZ STREAMLIT ---
st.set_page_config(layout="wide") 
st.title("🚀 Estrategia Golden: Predicciones BYMA")

if st.button("🔄 ACTUALIZAR MERCADO Y GENERAR PREDICCIONES"):
    with st.status("Procesando datos...", expanded=True) as status:
        st.write("Calculando niveles de entrada y salida...")
        extraer_todo_el_mercado()
        entrenar_modelo()
        generar_predicciones()
        status.update(label="✅ ¡Actualización Exitosa!", state="complete")
    st.rerun()

if os.path.exists(ruta_salida):
    df_mostrar = pd.read_excel(ruta_salida)
    
    # Definimos las columnas finales SIN la columna de Ratio
    columnas_finales = [
        'Ticker', 'Nombre', 'Sector', 'Precio', 'RSI', 
        'STOP LOSS', 'TP_CONSERVADOR', 'TP_OPTIMISTA', 'Confianza_%'
    ]
    
    st.subheader(f"📊 Listado Completo de Oportunidades ({len(df_mostrar)} activos)")
    st.dataframe(
        df_mostrar[columnas_finales],
        use_container_width=True,
        hide_index=True
    )

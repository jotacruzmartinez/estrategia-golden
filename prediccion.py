import streamlit as st
import pandas as pd
import pickle
import os
import subprocess

# CONFIGURACIÓN DE RUTAS
ruta_excel = 'HISTORIAL_DIARIO_COMPLETO.xlsx'
ruta_modelo = 'modelo_ia.pkl'
ruta_salida = 'TOP_10_PREDICCIONES.xlsx'

def generar_predicciones():
    if not os.path.exists(ruta_modelo):
        st.error("❌ El modelo no existe. Se requiere entrenamiento previo.")
        return

    df = pd.read_excel(ruta_excel)
    
    with open(ruta_modelo, 'rb') as f:
        modelo = pickle.load(f)

    # Preparamos los datos
    df['Distancia_MA50'] = df['Close'] / df['MA50']
    df['Distancia_MA200'] = df['Close'] / df['MA200']
    df['Volatilidad_Relativa'] = df['ATR'] / df['Close']
    
    ultima_data = df.sort_values('Date').groupby('Ticker').last().reset_index()
    columnas_ia = ['RSI', 'Distancia_MA50', 'Distancia_MA200', 'Volatilidad_Relativa']
    
    X_pred = ultima_data[columnas_ia].fillna(0)
    probs = modelo.predict_proba(X_pred)[:, 1]
    
    ultima_data['Confianza_%'] = (probs * 100).round(2)
    ultima_data['Stop_Loss'] = (ultima_data['Close'] - (ultima_data['ATR'] * 2)).round(2)
    ultima_data['Riesgo_Pesos'] = ultima_data['Close'] - ultima_data['Stop_Loss']
    ultima_data['Target_Sugerido'] = (ultima_data['Close'] + (ultima_data['Riesgo_Pesos'] * 1.5)).round(2)
    
    # Filtro: Confianza alta y volumen mínimo
    top_5 = ultima_data[ultima_data['Volume'] > 10].sort_values('Confianza_%', ascending=False).head(10)
    
    top_5.to_excel(ruta_salida, index=False)
    return top_5

# --- INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="Estrategia Golden", page_icon="⭐")
st.title("🚀 Estrategia Golden: Predicciones BYMA")

# Botón para ejecutar todo el proceso
if st.button("🔄 ACTUALIZAR MERCADO Y GENERAR PREDICCIONES"):
    with st.status("Procesando datos en la nube...", expanded=True) as status:
        st.write("1. Extrayendo datos de 402 activos (esto puede tardar)...")
        subprocess.run(["python", "pesos.py"], check=True)
        
        st.write("2. Entrenando la IA con mapa actualizado...")
        subprocess.run(["python", "IA.py"], check=True)
        
        st.write("3. Generando predicciones finales...")
        generar_predicciones()
        
        status.update(label="✅ ¡Todo actualizado con éxito!", state="complete", expanded=False)
    st.rerun()

st.divider()

# Mostrar la tabla si el archivo existe
if os.path.exists(ruta_salida):
    df_mostrar = pd.read_excel(ruta_salida)
    st.subheader("⭐ TOP 5 PARA MAÑANA")
    # Mostramos la tabla formateada y más estética
    st.dataframe(
        df_mostrar[['Ticker', 'Close', 'Confianza_%', 'Stop_Loss']].head(5),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Presioná el botón de arriba para generar el análisis del día.")

import streamlit as st
import pandas as pd
import pickle
import os

# Importamos TUS funciones originales de TUS otros archivos
from pesos import extraer_todo_el_mercado
from IA import entrenar_modelo

# CONFIGURACIÓN DE RUTAS (Las mismas que ya tenías)
ruta_excel = 'HISTORIAL_DIARIO_COMPLETO.xlsx'
ruta_modelo = 'modelo_ia.pkl'
ruta_salida = 'TOP_10_PREDICCIONES.xlsx'

def generar_predicciones():
    # AQUÍ ESTÁ TU LÓGICA EXACTA, NO CAMBIÉ NI UN CÁLCULO
    if not os.path.exists(ruta_modelo):
        st.error("❌ El modelo no existe.")
        return

    df = pd.read_excel(ruta_excel)
    with open(ruta_modelo, 'rb') as f:
        modelo = pickle.load(f)

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
    
    top_5 = ultima_data[ultima_data['Volume'] > 10].sort_values('Confianza_%', ascending=False).head(10)
    top_5.to_excel(ruta_salida, index=False)
    return top_5

# --- INTERFAZ ---
st.title("🚀 Estrategia Golden: Predicciones BYMA")

if st.button("🔄 ACTUALIZAR MERCADO Y GENERAR PREDICCIONES"):
    with st.status("Procesando...", expanded=True) as status:
        st.write("1. Ejecutando tu extracción de datos...")
        extraer_todo_el_mercado() # <--- Llama a tu función en pesos.py
        
        st.write("2. Ejecutando tu entrenamiento de IA...")
        entrenar_modelo() # <--- Llama a tu función en IA.py
        
        st.write("3. Calculando predicciones finales...")
        generar_predicciones()
        
        status.update(label="✅ ¡Completado!", state="complete")
    st.rerun()

if os.path.exists(ruta_salida):
    df_mostrar = pd.read_excel(ruta_salida)
    st.subheader("⭐ TOP 5 PARA MAÑANA")
    st.table(df_mostrar[['Ticker', 'Close', 'Confianza_%', 'Stop_Loss']].head(5))

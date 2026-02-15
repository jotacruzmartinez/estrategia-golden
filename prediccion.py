import pandas as pd
import pickle
import os

# CONFIGURACIÓN
ruta_excel = 'HISTORIAL_DIARIO_COMPLETO.xlsx'
ruta_modelo = 'modelo_ia.pkl'
ruta_salida = 'TOP_10_PREDICCIONES.xlsx'

def generar_predicciones():
    print("🔮 Generando predicciones para mañana...")
    
    if not os.path.exists(ruta_modelo):
        print("❌ El modelo no existe. Corré ia.py primero.")
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
    ultima_data['Stop_Loss'] = ultima_data['Close'] - (ultima_data['ATR'] * 2)
    ultima_data['Riesgo_Pesos'] = ultima_data['Close'] - ultima_data['Stop_Loss']
    ultima_data['Target_Sugerido'] = ultima_data['Close'] + (ultima_data['Riesgo_Pesos'] * 1.5)
    
    # Filtro: Confianza alta y volumen mínimo para evitar "papeles fantasma"
    top_5 = ultima_data[ultima_data['Volume'] > 10].sort_values('Confianza_%', ascending=False).head(10)
    
    top_5.to_excel(ruta_salida, index=False)
    print(f"✅ Top 10 generado.")
    print("\n⭐ TOP 5 PARA MAÑANA:")
    print(top_5[['Ticker', 'Close', 'Confianza_%', 'Stop_Loss']].head(5))

if __name__ == "__main__":

    generar_predicciones()

import streamlit as st
import subprocess

if __name__ == "__main__":
    st.title("⭐ TOP 5 PARA MAÑANA")
    
    # Botón para ejecutar todo el proceso
    if st.button("🔄 ACTUALIZAR MERCADO Y GENERAR PREDICCIONES"):
        with st.status("Ejecutando proceso completo...", expanded=True) as status:
            st.write("1. Extrayendo datos de 402 activos (pesos.py)...")
            subprocess.run(["python", "pesos.py"])
            
            st.write("2. Entrenando la IA (IA.py)...")
            subprocess.run(["python", "IA.py"])
            
            st.write("3. Generando predicciones finales...")
            generar_predicciones()
            
            status.update(label="✅ ¡Proceso Completado!", state="complete", expanded=False)

    # Mostrar la tabla si el archivo existe
    if os.path.exists(ruta_salida):
        df_mostrar = pd.read_excel(ruta_salida)
        st.subheader("Resultados del análisis:")
        st.table(df_mostrar[['Ticker', 'Close', 'Confianza_%', 'Stop_Loss']].head(5))
    else:
        st.info("Hacé clic en el botón de arriba para iniciar el análisis por primera vez.")



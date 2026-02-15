import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

# CONFIGURACIÓN
ruta_excel = 'HISTORIAL_DIARIO_COMPLETO.xlsx'
ruta_modelo = 'modelo_ia.pkl'

def entrenar_modelo():
    print("🧠 Entrenando la IA con el nuevo mapa de mercado...")
    
    if not os.path.exists(ruta_excel):
        print("❌ No se encuentra el Excel. Corré pesos.py primero.")
        return

    df = pd.read_excel(ruta_excel)
    
    # Creamos variables inteligentes (Features)
    df['Distancia_MA50'] = df['Close'] / df['MA50']
    df['Distancia_MA200'] = df['Close'] / df['MA200']
    df['Volatilidad_Relativa'] = df['ATR'] / df['Close']
    
    # Objetivo: ¿Subió el precio en los próximos 5 días?
    df['Target'] = (df.groupby('Ticker')['Close'].shift(-5) > df['Close']).astype(int)
    
    columnas_ia = ['RSI', 'Distancia_MA50', 'Distancia_MA200', 'Volatilidad_Relativa']
    
    # Limpieza de nulos
    df_train = df.dropna(subset=columnas_ia + ['Target'])
    
    X = df_train[columnas_ia]
    y = df_train['Target']
    
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X, y)
    
    with open(ruta_modelo, 'wb') as f:
        pickle.dump(modelo, f)
    
    print(f"✅ IA Re-entrenada con éxito.")

if __name__ == "__main__":

    entrenar_modelo()

import yfinance as yf
import pandas as pd
import pandas_ta as ta
import os

# CONFIGURACIÓN
ruta_excel = 'HISTORIAL_DIARIO_COMPLETO.xlsx'

def extraer_todo_el_mercado():
    print("🚀 Iniciando extracción masiva de CEDEARs (Pesos Argentinos)...")
    
    # 1. Obtenemos una lista extendida de CEDEARs conocidos y tickers locales
    # Usamos el sufijo .BA para asegurar que traiga PESOS de la Bolsa de Comercio de Bs As
    tickers_base = [
        'MMM', 'ABT', 'ABBV', 'ANF', 'ACN', 'ADGO', 'ADS', 'ADBE', 'JMIA', 'AAP', 
        'AMD', 'AEG', 'AEM', 'ABNB', 'BABA', 'GOOGL', 'AABA', 'MO', 'AOCA', 'AMZN', 
        'ABEV', 'ABEV3', 'AMX', 'AAL', 'AXP', 'AIG', 'AMGN', 'ADI', 'AAPL', 'AMAT', 
        'ARCO', 'ARKK', 'ARM', 'ASML', 'ASTS', 'ALAB', 'AZN', 'T', 'TEAM', 'ADP', 
        'AVY', 'CAR', 'BIDU', 'BKR', 'BBD', 'BBDC3', 'BBAS3', 'ITUB3', 'BSBR', 'SAN', 
        'BA.C', 'BCS', 'B', 'BAS', 'BAYN', 'BRKB', 'BHP', 'BBV', 'BIOX', 'BIIB', 
        'BITF', 'BB', 'BKNG', 'BP', 'LND', 'BAK', 'BRFS', 'BMY', 'AVGO', 'BNG', 
        'AI', 'CAT', 'CAH', 'CCL', 'CLS', 'CX', 'EBR', 'SCHW', 'CVX', 'LFC', 
        'SNP', 'SBSP3', 'CSCO', 'C', 'KOFM', 'CDE', 'COIN', 'CL', 'CBRD', 'SBS', 
        'ELP', 'SID', 'CSNA3', 'CEG', 'CRWV', 'GLW', 'CAAP', 'COST', 'CS', 'CVS', 
        'DHR', 'BSN', 'DECK', 'DE', 'DAL', 'DTEA', 'DEO', 'SPXL', 'DOCU', 'DOW', 
        'DD', 'EOAN', 'EBAY', 'ECL', 'EA', 'LLY', 'AKO.B', 'ERJ', 'XLE', 'E', 
        'EFX', 'EQNR', 'GLD', 'ETSY', 'XOM', 'FNMA', 'FDX', 'RACE', 'XLF', 'FSLR', 
        'XLU', 'FMX', 'F', 'FMCC', 'FCX', 'GRMN', 'GE', 'GM', 'GPRK', 'GGB', 
        'GILD', 'URA', 'GLOB', 'GFI', 'GT', 'PAC', 'ASR', 'TV', 'GSK', 'HAL', 
        'HAPV3', 'HOG', 'HMY', 'HDB', 'HL', 'HHPD', 'HMC', 'HON', 'HWM', 'HPQ', 
        'HSBC', 'HNPIY', 'HUT', 'IBN', 'INFY', 'ING', 'INTC', 'IBM', 'IFF', 'IP', 
        'ISRG', 'QQQ', 'VXX', 'IREN', 'IBIT', 'FXI', 'IEMG', 'IEUR', 'IWDA', 'JH', 
        'ETHA', 'ACWI', 'EWZ', 'EFA', 'EEM', 'EWJ', 'IBB', 'IVW', 'IVE', 'SLV', 
        'IWM', 'ITA', 'ITUB', 'JPM', 'JD', 'JNJ', 'JCI', 'JOYY', 'KB', 'KMB', 
        'KGC', 'PHG', 'KEP', 'MRVL', 'LRCX', 'LVS', 'LAR', 'LAC', 'LYO', 'ERIC', 
        'RENT3', 'LMT', 'LREN3', 'MGLU3', 'MMC', 'MA', 'MCD', 'MUX', 'MDT', 'MELI', 
        'MBG', 'MRK', 'META', 'MU', 'MSFT', 'MSTR', 'MUFG', 'MFG', 'MBT', 'MRNA', 
        'MDLZ', 'MSI', 'NGG', 'NTCO', 'NTCO3', 'NECT', 'NTES', 'NFLX', 'NEM', 'NXE', 
        'NKE', 'NIO', 'NSAN', 'NOKA', 'NMR', 'NG', 'NVS', 'NLM', 'UN', 'NUE', 
        'NVDA', 'OXY', 'OKLO', 'ORCL', 'ORAN', 'ORLY', 'PCAR', 'PAGS', 'PLTR', 'PANW', 
        'PAAS', 'PCRF', 'PYPL', 'PDD', 'PSO', 'PEP', 'PRIO3', 'PETR3', 'PBR', 'PTR', 
        'PFE', 'PM', 'PSX', 'PINS', 'PBI', 'OGZD', 'LKOD', 'ATAD', 'PKS', 'PG', 
        'SH', 'PSQ', 'TQQQ', 'QCOM', 'RTX', 'RCTI', 'RIO', 'RIOT', 'HOOD', 'RBLX', 
        'RKLB', 'ROKU', 'ROST', 'SHEL', 'SPGI', 'CRM', 'SMSN', 'SAP', 'SATL', 'SLB', 
        'SE', 'NOW', 'SHPW', 'SHOP', 'SIEGY', 'SI', 'SWKS', 'SNAP', 'SNA', 'SNOW', 
        'SONY', 'SCCO', 'DIA', 'SPY', 'SPOT', 'XYZ', 'SBUX', 'STLA', 'STNE', 'SDA', 
        'SUZ', 'SUZB3', 'SYY', 'TSM', 'TGT', 'TTM', 'RCTB4', 'TILAY', 'VIV', 'VIVT3', 
        'TEFO', 'TEM', 'TEN', 'TXR', 'TSLA', 'TXN', 'BK', 'BA', 'KO', 'XLC', 
        'XLY', 'XLP', 'GS', 'XLV', 'HSY', 'HD', 'XLI', 'XLB', 'MOS', 'XLRE', 
        'XLK', 'TRVV', 'DISN', 'TMO', 'TIMB', 'TIMS3', 'TJX', 'TMUS', 'TTE', 'TM', 
        'TCOM', 'TRIP', 'TWLO', 'TWTR', 'USB', 'UBER', 'PATH', 'UGP', 'UL', 'UNP', 
        'UAL', 'USO', 'UNH', 'UPST', 'URBN', 'XLU', 'VALE', 'VALE3', 'GDX', 'SMH', 
        'VIG', 'VEA', 'VRSN', 'VZ', 'VRTX', 'SPCE', 'V', 'VIST', 'VST', 'VOD', 
        'WBA', 'WMT', 'WEGE3', 'WBO', 'WFC', 'XROX', 'XP', 'XPEV', 'AUY', 'YZCA', 
        'YELP', 'ZM'
    ]
    
    # Agregamos el sufijo .BA a todos para forzar PESOS
    tickers_ba = [t + ".BA" for t in tickers_base]
    
    todas_las_datas = []

    for ticker in tickers_ba:
        try:
            # 1. Creamos el objeto ticker para obtener info extra
            t_obj = yf.Ticker(ticker)
            
            # 2. Bajamos el historial
            data = t_obj.history(period="2y", interval="1d")
            
            if data.empty or len(data) < 200:
                continue

            # Limpiar columnas
            data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
            
            # 3. Obtenemos Nombre y Sector
            # Si Yahoo no lo tiene, ponemos 'N/A'
            nombre = t_obj.info.get('longName', 'N/A')
            sector = t_obj.info.get('sector', 'N/A')
            
            # --- CÁLCULO DE INDICADORES ---
            data['RSI'] = ta.rsi(data['Close'], length=14)
            data['MA50'] = ta.sma(data['Close'], length=50)
            data['MA200'] = ta.sma(data['Close'], length=200)
            data['ATR'] = ta.atr(data['High'], data['Low'], data['Close'], length=14)
            
            # --- LIMPIEZA Y FORMATO ---
            ticker_nom = ticker.replace(".BA", "")
            data['Ticker'] = ticker_nom
            data['Nombre'] = nombre
            data['Sector'] = sector
            data['Date'] = data.index
            
            # Seleccionamos las columnas (Agregamos Nombre y Sector)
            df_ticker = data[['Ticker', 'Nombre', 'Sector', 'Date', 'Close', 'High', 'Low', 'Open', 'Volume', 'RSI', 'MA50', 'MA200', 'ATR']]
            
            if pd.isna(df_ticker['Close'].iloc[-1]):
                continue

            todas_las_datas.append(df_ticker.tail(300))
            print(f"✅ {ticker_nom} procesado.")

        except Exception as e:
            print(f"❌ Error en {ticker}: {e}")

    if todas_las_datas:
        df_final = pd.concat(todas_las_datas)
        df_final.to_excel(ruta_excel, index=False)
        print(f"\n🔥 EXTRACCIÓN MASIVA COMPLETADA 🔥")
    else:
        print("🔴 No se pudo extraer nada.")

if __name__ == "__main__":
    extraer_todo_el_mercado()

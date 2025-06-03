import pandas as pd

# Cargar la tabla de mortalidad

df_mortalidad = pd.read_csv("C:\\Users\\celes\\OneDrive\\Actuariales\\ALTUM\\Mortalidad.csv")

ruta = r"C:\Users\celes\OneDrive\Actuariales\ALTUM\Mortalidad.csv"
df_mortalidad = pd.read_csv(ruta)

def qx(age, df_mort):
    fila = df_mort.loc[df_mort['Edad'] == age]
    if not fila.empty:
        return float(fila['Muerte'].values[0])
    else:
        # Caso en que no se encuentra la edad: se asume probabilidad de muerte 1
        return 1

def edadn(edad, sexo, status):
    ajuste = 0
    if sexo.lower() == "femenino":
        ajuste += 3
    if status.lower() == "no fumador":
        ajuste += 2
    return edad - ajuste

def crec_SA(SA, tipo_crecimiento, n):
    # Convertir a string para aplicar .lower()
    tc = str(tipo_crecimiento).lower()
    if tc == "na":
        return SA
    elif tc == "fijo":
        return SA * (1 + 0.05 * n)
    elif tc == "variable":
        return SA * (1.05 ** n)
    else:
        return SA

def prima_neta_individual(producto, cobertura, edad, SAF, tipo_crecimiento, SAD):
    prob_survive = 1
    prima = 0
    producto = producto.lower()
    if producto == "temporal":
        for k in range(cobertura):
            q = qx(edad + k, df_mortalidad)
            prima += crec_SA(SAF, tipo_crecimiento, k) * (1.05 ** (-(k + 1))) * prob_survive * q
            prob_survive *= (1 - q)
        return prima
    elif producto == "ordinario de vida":
        for k in range(112 - edad):
            q = qx(edad + k, df_mortalidad)
            prima += crec_SA(SAF, tipo_crecimiento, k) * (1.05 ** (-(k + 1))) * prob_survive * q
            prob_survive *= (1 - q)
        return prima
    elif producto == "dotal mixto":
        # Se calcula la probabilidad acumulada de supervivencia durante la cobertura
        for k in range(cobertura):
            q = qx(edad + k, df_mortalidad)
            prob_survive *= (1 - q)
        primaDot = prob_survive * SAD * (1.05 ** (-cobertura))
        # Se calcula la parte de prima temporal (que cubre la muerte durante la cobertura)
        primaTem = prima_neta_individual("temporal", cobertura, edad, SAF, tipo_crecimiento, SAD)
        return primaDot + primaTem
    else:
        return 0

def anualiad(pagos, edad, df_mortalidad):
    producto = 0
    prob_survive = 1
    if pagos != 0 :
        for k in range(pagos):
            q = qx(edad + k, df_mortalidad)
            producto += (1.05 ** (-k)) * prob_survive
            prob_survive *= (1 - q)
        return producto
    else: 
        return 0 

def kqx1x2_VC(edad1, edad2, cobertura):
    prob_survive1 = 1
    prob_survive2 = 1
    for k in range(cobertura):
        q1 = qx(edad1 + k, df_mortalidad)
        q2 = qx(edad2 + k, df_mortalidad)
        q12 = prob_survive1 * prob_survive2 * (1 - (1 - q1) * (1 - q2))
        prob_survive1 *= (1 - q1)
        prob_survive2 *= (1 - q2)
    return q12

def Prima_neta_VC(producto, cobertura, edad1, edad2, SAF, SAD, tipo_crecimiento):
    prima = 0
    if producto.lower() == "temporal":
        for k in range(cobertura):
            SA_k = crec_SA(SAF, tipo_crecimiento, k)
            Vk = (1.05) ** (-(k + 1))
            prima += SA_k * Vk * kqx1x2_VC(edad1, edad2, k + 1)
        return prima
    elif producto.lower() == "ordinario de vida":
        edad_max_tabla = 112
        cobertura_calc = edad_max_tabla - max(edad1, edad2)
        for k in range(cobertura_calc):
            SA_k = crec_SA(SAF, tipo_crecimiento, k)
            Vk = (1.05) ** (-(k + 1))
            prima += SA_k * Vk * kqx1x2_VC(edad1, edad2, k + 1)
        return prima
    elif producto.lower() == "dotal mixto":
        prob_survive1 = 1
        prob_survive2 = 1
        for k in range(cobertura):
            q1 = qx(edad1 + k, df_mortalidad)
            q2 = qx(edad2 + k, df_mortalidad)
            prob_survive1 *= (1 - q1)
            prob_survive2 *= (1 - q2)
        PrimaTemp = Prima_neta_VC("temporal", cobertura, edad1, edad2, SAF, SAD, tipo_crecimiento)
        PrimaDot = SAD * prob_survive1 * prob_survive2 * (1.05 ** (-cobertura))
        return PrimaTemp + PrimaDot
    else:
        return 0

def anualidad_VC(pagos, edad1, edad2, df_mortalidad):
    prob_survive1 = 1
    prob_survive2 = 1
    producto_An = 0
    for k in range(pagos):
        q1 = qx(edad1 + k, df_mortalidad)
        q2 = qx(edad2 + k, df_mortalidad)
        producto_An += prob_survive1 * prob_survive2 * (1.05 ** (-k))
        prob_survive1 *= (1 - q1)
        prob_survive2 *= (1 - q2)
    return producto_An

def kqx1x2_US(edad1, edad2, cobertura):
    prob_survive1 = 1
    prob_survive2 = 1
    for k in range(cobertura):
        q1 = qx(edad1 + k, df_mortalidad)
        q2 = qx(edad2 + k, df_mortalidad)
        q12 = (1 - (1 - prob_survive1) * (1 - prob_survive2)) * q1 * q2
        prob_survive1 *= (1 - q1)
        prob_survive2 *= (1 - q2)
    return q12

def Prima_neta_US(producto, cobertura, edad1, edad2, SAF, SAD, tipo_crecimiento):
    prima = 0
    if producto.lower() == "temporal":
        for k in range(cobertura):
            SA_k = crec_SA(SAF, tipo_crecimiento, k)
            Vk = (1.05) ** (-(k + 1))
            prima += SA_k * Vk * kqx1x2_US(edad1, edad2, k + 1)
        return prima
    elif producto.lower() == "ordinario de vida":
        edad_max_tabla = 112  
        cobertura_calc = edad_max_tabla - max(edad1, edad2)
        for k in range(cobertura_calc):
            SA_k = crec_SA(SAF, tipo_crecimiento, k)
            Vk = (1.05) ** (-(k + 1))
            prima += SA_k * Vk * kqx1x2_US(edad1, edad2, k + 1)
        return prima 
    elif producto.lower() == "dotal mixto":
        prob_survive1 = 1
        prob_survive2 = 1
        for k in range(cobertura):
            q1 = qx(edad1 + k, df_mortalidad)
            q2 = qx(edad2 + k, df_mortalidad)
            prob_survive1 *= (1 - q1)
            prob_survive2 *= (1 - q2)
        PrimaTemp = Prima_neta_US("temporal", cobertura, edad1, edad2, SAF, SAD, tipo_crecimiento)
        PrimaDot = SAD * (1 - (1 - prob_survive1) * (1 - prob_survive2)) * (1.05 ** (-cobertura))
        return PrimaTemp + PrimaDot
    else:
        return 0

def anualidad_US(pagos, edad1, edad2, df_mortalidad):
    prob_survive1 = 1
    prob_survive2 = 1
    producto_An = 0
    for k in range(pagos):
        q1 = qx(edad1 + k, df_mortalidad)
        q2 = qx(edad2 + k, df_mortalidad)
        producto_An += (1 - (1 - prob_survive1) * (1 - prob_survive2)) * (1.05 ** (-k))
        prob_survive1 *= (1 - q1)
        prob_survive2 *= (1 - q2)
    return producto_An

def insumos_PNU_PA(tipo, producto, cobertura, pagos, edad1, edad2, SAF, tipo_crecimiento, SAD):
    tipo = tipo.lower()
    if tipo == "individual":
        pnu = prima_neta_individual(producto, cobertura, edad1, SAF, tipo_crecimiento, SAD)
        factor_anualidad = anualiad(pagos, edad1, df_mortalidad)
        pa = pnu / factor_anualidad if factor_anualidad != 0 else 0
    elif tipo == "vida conjunta":  # Vida Conjunta (primera muerte)
        pnu = Prima_neta_VC(producto, cobertura, edad1, edad2, SAF, SAD, tipo_crecimiento)
        factor_anualidad = anualidad_VC(pagos, edad1, edad2, df_mortalidad)
        pa = pnu / factor_anualidad if factor_anualidad != 0 else 0
    elif tipo == "ultimo superviviente":  # Último Superviviente
        pnu = Prima_neta_US(producto, cobertura, edad1, edad2, SAF, SAD, tipo_crecimiento)
        factor_anualidad = anualidad_US(pagos, edad1, edad2, df_mortalidad)
        pa = pnu / factor_anualidad if factor_anualidad != 0 else 0
    else:
        pnu = 0
        pa = 0
    return pnu, pa

def Reservas(tipo, producto, cobertura, pagos, edad1, edad2, SAF, tipo_crecimiento, SAD, PA):
    tipo = tipo.lower()
    if tipo == "individual":
        pnu = prima_neta_individual(producto, cobertura, edad1, SAF, tipo_crecimiento, SAD)
        factor_anualidad = anualiad(pagos, edad1, df_mortalidad)
        Reserva = pnu - factor_anualidad * PA 
    elif tipo == "vida conjunta":  # Vida Conjunta (primera muerte)
        pnu = Prima_neta_VC(producto, cobertura, edad1, edad2, SAF, SAD, tipo_crecimiento)
        factor_anualidad = anualidad_VC(pagos, edad1, edad2, df_mortalidad)
        Reserva = pnu - factor_anualidad * PA 
       

    elif tipo == "ultimo superviviente":  # Último Superviviente
        pnu = Prima_neta_US(producto, cobertura, edad1, edad2, SAF, SAD, tipo_crecimiento)
        factor_anualidad = anualidad_US(pagos, edad1, edad2, df_mortalidad)
        Reserva = pnu - factor_anualidad * PA 
    else:
        pnu = 0
        Reserva = 0

    
    return Reserva,pnu 

#Procesamiento del archivo de pólizas y guardado de resultados
ruta_polizas = r"C:\Users\celes\OneDrive\Desktop\Resultados_reservas.csv"
df_polizas = pd.read_csv(ruta_polizas)

def aplicar_insumos(row):
    Reserva,npnu = Reservas(
        row['Tipo'],
        row['Producto'],
        row['Cobertura'],
        row['Pagos'],
        row['Edad1'],
        row['Edad2'],
        row[' SAF '],
        row['Crecimiento'],
        row['SAD'],
        row['PA']
    )
    return pd.Series({'RRC': Reserva, 'npnu': npnu })



df_polizas[['RRC','npnu']] = df_polizas.apply(aplicar_insumos, axis=1)

ruta_resultados = r"C:\Users\celes\OneDrive\Desktop\Resultados_reservas.csv"
df_polizas.to_csv(ruta_resultados, index=False)

print("Cálculo completado y resultados guardados en", ruta_resultados)

#print(list(df_polizas.columns))

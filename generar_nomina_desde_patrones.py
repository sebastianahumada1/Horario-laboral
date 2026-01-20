#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar el CSV de nómina completo a partir de los patrones identificados
"""

import json
import csv
from datetime import datetime, timedelta
import calendar

def es_festivo(fecha, festivos=None):
    """Determina si una fecha es festiva (simplificado - puedes agregar lista de festivos)"""
    # Por ahora, solo verifica si es domingo
    # Puedes agregar una lista de festivos específicos
    if festivos:
        fecha_str = fecha.strftime('%d/%m/%y')
        return fecha_str in festivos
    return False

def obtener_tipo_dia(fecha):
    """Obtiene el tipo de día (Laboral, Festivo, Domingo)"""
    dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
    
    if dia_semana == 6:  # Domingo
        return 'Domingo'
    elif es_festivo(fecha):
        return 'Festivo'
    else:
        return 'Laboral'

# Fechas de inicio del ciclo para cada empleado con patrón rotación
FECHAS_INICIO_CICLO = {
    'Daniel Alfonso Lara Torres': datetime.strptime('17/12/24', '%d/%m/%y')  # Miércoles 17 dic - día 1 del ciclo
}

def obtener_dia_ciclo_empleado(empleado, fecha):
    """
    Obtiene el día del ciclo específico para un empleado (1-14)
    Cada empleado tiene su propio ciclo de 14 días:
    - Días 1-10: trabaja
    - Días 11-14: descansa
    """
    nombre = empleado['nombre']
    
    if empleado.get('rotacion_mi_vi') and nombre in FECHAS_INICIO_CICLO:
        fecha_inicio_empleado = FECHAS_INICIO_CICLO[nombre]
    else:
        # Si no tiene fecha específica, usar fecha inicio general (para otros empleados)
        fecha_inicio_empleado = datetime.strptime('17/12/24', '%d/%m/%y')
    
    # Normalizar fechas a medianoche para evitar problemas de horas
    fecha_inicio_norm = fecha_inicio_empleado.replace(hour=0, minute=0, second=0, microsecond=0)
    fecha_norm = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
    
    delta = fecha_norm - fecha_inicio_norm
    dias_desde_inicio = delta.days
    
    # Calcular día del ciclo (1-14)
    # días_desde_inicio = 0 significa día 1 del ciclo
    # días_desde_inicio = 1 significa día 2 del ciclo
    # días_desde_inicio = n significa día n+1 del ciclo
    # Aplicar módulo 14 y sumar 1 para obtener día del ciclo (1-14)
    dia_ciclo = ((dias_desde_inicio % 14) + 14) % 14
    dia_ciclo = dia_ciclo + 1  # dias_desde_inicio 0 = día 1, dias_desde_inicio 1 = día 2, etc.
    
    return dia_ciclo

def esta_trabajando_en_ciclo(dia_ciclo):
    """Determina si un empleado está trabajando según el día del ciclo"""
    # Días 1-10: trabaja
    # Días 11-14: descansa
    return 1 <= dia_ciclo <= 10

def determinar_grupo_semana(fecha_inicio, fecha):
    """Determina qué grupo trabaja en una semana específica (para patrones normales)"""
    # Calcular número de semana desde fecha inicio
    delta = fecha - fecha_inicio
    semanas = delta.days // 7
    
    # Alternar entre A y B cada semana
    # Si semanas es par -> A, si es impar -> B
    return 'A' if semanas % 2 == 0 else 'B'

def generar_nomina(archivo_patrones, fecha_inicio, fecha_fin, archivo_salida):
    """Genera el CSV de nómina completo desde fecha_inicio hasta fecha_fin"""
    
    # Cargar patrones
    with open(archivo_patrones, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Parsear fechas
    fecha_ini = datetime.strptime(fecha_inicio, '%d/%m/%y')
    fecha_end = datetime.strptime(fecha_fin, '%d/%m/%y')
    
    # Preparar datos de empleados
    empleados = {}
    for emp in config['empleados']:
        empleados[emp['nombre']] = emp
    
    # Generar filas
    filas = []
    
    fecha_actual = fecha_ini
    while fecha_actual <= fecha_end:
        dia_semana_num = fecha_actual.weekday() + 1  # 1=Lunes, 7=Domingo
        tipo_dia = obtener_tipo_dia(fecha_actual)
        semana_num = fecha_actual.isocalendar()[1]
        mes = fecha_actual.month
        
        # Determinar grupo activo esta semana (para patrones normales)
        grupo_activo = determinar_grupo_semana(fecha_ini, fecha_actual)
        
        for nombre, datos_emp in empleados.items():
            # Verificar si este empleado trabaja este día
            trabaja = False
            
            # Días que SIEMPRE trabajan ambos (Miércoles, Jueves, Viernes)
            dias_mi_vi = [3, 4, 5]  # Miércoles, Jueves, Viernes
            
            # Días que alternan (Sábado, Domingo, Lunes, Martes)
            dias_alternos = [6, 7, 1, 2]  # Sábado, Domingo, Lunes, Martes
            
            # PATRÓN ESPECIAL: Rotación 10 días trabajo / 4 días descanso (Daniel y Juan)
            es_patron_rotacion = datos_emp.get('rotacion_mi_vi', False)
            
            if es_patron_rotacion:
                # PATRÓN: 10 días trabajo / 4 días descanso
                # Cada empleado tiene su propio ciclo de 14 días independiente:
                # - Días 1-10: trabaja (todos los días)
                # - Días 11-14: descansa (todos los días)
                dia_ciclo_empleado = obtener_dia_ciclo_empleado(datos_emp, fecha_actual)
                trabaja = esta_trabajando_en_ciclo(dia_ciclo_empleado)
            else:
                # Patrón normal: usar patrón semanal base
                if str(dia_semana_num) in datos_emp['patron_semanal']:
                    trabaja_base = datos_emp['patron_semanal'][str(dia_semana_num)]
                else:
                    trabaja_base = False
                
                grupo_coincide = (datos_emp['grupo'] == grupo_activo)
                
                # Verificar festivos y domingos
                if tipo_dia == 'Festivo':
                    trabaja = trabaja_base and datos_emp['trabaja_festivos'] and grupo_coincide
                elif tipo_dia == 'Domingo':
                    trabaja = trabaja_base and datos_emp['trabaja_domingos'] and grupo_coincide
                else:
                    trabaja = trabaja_base and grupo_coincide
            
            # Valor: 9 si trabaja, 0 si no
            valor = '9' if trabaja else '0'
            
            # Preparar fila (simplificada - solo columnas esenciales)
            fila = [
                '',  # Analista (vacío por ahora)
                nombre,
                datos_emp['horario'],
                fecha_actual.strftime('%d/%m/%y'),
                valor,
                str(mes),
                str(semana_num),
                datos_emp['grupo'],
                str(dia_semana_num),
                tipo_dia
            ]
            
            filas.append(fila)
        
        fecha_actual += timedelta(days=1)
    
    # Escribir CSV
    with open(archivo_salida, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        
        # Encabezado simplificado
        writer.writerow([
            'Analista',
            'Nombre',
            'Rango Horario',
            'Fecha',
            'Valor',
            'Mes',
            'semana',
            'Grupo',
            'Dia de semana',
            'Festivo'
        ])
        
        # Escribir filas
        for fila in filas:
            writer.writerow(fila)
    
    print(f"✓ Nómina generada: {archivo_salida}")
    print(f"  Período: {fecha_inicio} a {fecha_fin}")
    print(f"  Total de registros: {len(filas)}")

def main():
    archivo_patrones = 'patrones_nomina.json'
    
    # Ejemplo: generar para un período específico
    fecha_inicio = input("Fecha inicio (DD/MM/YY) o Enter para usar 17/12/24: ").strip()
    if not fecha_inicio:
        fecha_inicio = '17/12/24'  # Fecha de inicio del ciclo: 17 dic 2024 (miércoles)
    
    fecha_fin = input("Fecha fin (DD/MM/YY) o Enter para usar 31/12/26: ").strip()
    if not fecha_fin:
        fecha_fin = '31/12/26'
    
    archivo_salida = f'nomina_generada_{fecha_inicio.replace("/", "_")}_a_{fecha_fin.replace("/", "_")}.csv'
    
    generar_nomina(archivo_patrones, fecha_inicio, fecha_fin, archivo_salida)

if __name__ == '__main__':
    main()


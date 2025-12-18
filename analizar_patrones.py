#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analizar patrones de nómina y generar configuración simplificada
"""

import csv
from collections import defaultdict
from datetime import datetime
import json

def parse_fecha(fecha_str):
    """Convierte fecha DD/MM/YY a objeto datetime"""
    try:
        return datetime.strptime(fecha_str, '%d/%m/%y')
    except:
        return None

def analizar_patrones(archivo_csv):
    """Analiza el CSV y extrae patrones por empleado"""
    
    patrones = defaultdict(lambda: {
        'horario': None,
        'grupo': None,
        'dias_trabajo': defaultdict(int),  # día de semana -> conteo
        'dias_no_trabajo': defaultdict(int),
        'trabaja_festivos': False,
        'trabaja_domingos': False,
        'patron_semanal': {}  # día semana -> trabaja (True/False)
    })
    
    with open(archivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)  # Saltar encabezado
        
        for row in reader:
            if len(row) < 10:
                continue
                
            nombre = row[1].strip()
            horario = row[2].strip()
            fecha_str = row[3].strip()
            valor = row[4].strip()
            grupo = row[7].strip()
            dia_semana = row[8].strip()
            tipo_dia = row[9].strip()
            
            if not nombre or not horario:
                continue
            
            # Guardar horario y grupo
            if not patrones[nombre]['horario']:
                patrones[nombre]['horario'] = horario
            if not patrones[nombre]['grupo']:
                patrones[nombre]['grupo'] = grupo
            
            # Analizar si trabaja o no
            trabaja = (valor == '9')
            dia_num = int(dia_semana) if dia_semana.isdigit() else None
            
            if dia_num:
                if trabaja:
                    patrones[nombre]['dias_trabajo'][dia_num] += 1
                else:
                    patrones[nombre]['dias_no_trabajo'][dia_num] += 1
            
            # Verificar festivos y domingos
            if tipo_dia == 'Festivo' and trabaja:
                patrones[nombre]['trabaja_festivos'] = True
            if tipo_dia == 'Domingo' and trabaja:
                patrones[nombre]['trabaja_domingos'] = True
    
    # Determinar patrón semanal
    for nombre, datos in patrones.items():
        for dia in range(1, 8):  # 1=Lunes, 7=Domingo
            trabaja_count = datos['dias_trabajo'].get(dia, 0)
            no_trabaja_count = datos['dias_no_trabajo'].get(dia, 0)
            
            # Si trabaja más del 50% de las veces, considera que trabaja ese día
            total = trabaja_count + no_trabaja_count
            if total > 0:
                porcentaje = trabaja_count / total
                datos['patron_semanal'][dia] = porcentaje > 0.5
    
    return patrones

def generar_configuracion(patrones):
    """Genera archivo de configuración simplificado"""
    
    config = {
        'empleados': []
    }
    
    for nombre, datos in sorted(patrones.items()):
        # Determinar días laborales
        dias_laborales = [dia for dia, trabaja in sorted(datos['patron_semanal'].items()) if trabaja]
        
        # Formatear días de la semana
        dias_nombres = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 
                       5: 'Viernes', 6: 'Sábado', 7: 'Domingo'}
        dias_texto = [dias_nombres[dia] for dia in dias_laborales]
        
        empleado = {
            'nombre': nombre,
            'horario': datos['horario'],
            'grupo': datos['grupo'],
            'dias_laborales': dias_laborales,
            'dias_laborales_texto': dias_texto,
            'trabaja_festivos': datos['trabaja_festivos'],
            'trabaja_domingos': datos['trabaja_domingos'],
            'patron_semanal': datos['patron_semanal']
        }
        
        config['empleados'].append(empleado)
    
    return config

def generar_csv_simplificado(config, archivo_salida):
    """Genera un CSV simplificado con los patrones"""
    
    with open(archivo_salida, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        
        # Encabezado
        writer.writerow([
            'Nombre',
            'Horario',
            'Grupo',
            'Días Laborales',
            'Trabaja Festivos',
            'Trabaja Domingos',
            'Patrón Semanal (L=1, M=2, X=3, J=4, V=5, S=6, D=7)'
        ])
        
        for emp in config['empleados']:
            dias_str = ', '.join(emp['dias_laborales_texto'])
            patron_str = ', '.join([f"{dia}:{'Sí' if trabaja else 'No'}" 
                                   for dia, trabaja in sorted(emp['patron_semanal'].items())])
            
            writer.writerow([
                emp['nombre'],
                emp['horario'],
                emp['grupo'],
                dias_str,
                'Sí' if emp['trabaja_festivos'] else 'No',
                'Sí' if emp['trabaja_domingos'] else 'No',
                patron_str
            ])

def main():
    archivo_entrada = 'Propuesta de Turno SEP Analistas 1 - NO TOCAR.csv'
    archivo_json = 'patrones_nomina.json'
    archivo_csv_salida = 'patrones_nomina_simplificado.csv'
    
    print("Analizando patrones de nómina...")
    patrones = analizar_patrones(archivo_entrada)
    
    print(f"Encontrados {len(patrones)} empleados")
    
    print("\nGenerando configuración...")
    config = generar_configuracion(patrones)
    
    # Guardar JSON
    with open(archivo_json, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"✓ Configuración guardada en: {archivo_json}")
    
    # Guardar CSV simplificado
    generar_csv_simplificado(config, archivo_csv_salida)
    print(f"✓ CSV simplificado guardado en: {archivo_csv_salida}")
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("RESUMEN DE PATRONES")
    print("="*80)
    
    for emp in config['empleados']:
        print(f"\n{emp['nombre']}")
        print(f"  Horario: {emp['horario']}")
        print(f"  Grupo: {emp['grupo']}")
        print(f"  Días laborales: {', '.join(emp['dias_laborales_texto'])}")
        print(f"  Trabaja festivos: {'Sí' if emp['trabaja_festivos'] else 'No'}")
        print(f"  Trabaja domingos: {'Sí' if emp['trabaja_domingos'] else 'No'}")

if __name__ == '__main__':
    main()


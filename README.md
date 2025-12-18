# Sistema de Gestión de Nómina por Patrones

Este sistema simplifica la gestión de nómina analizando los patrones de trabajo de cada empleado y generando automáticamente los registros basándose en reglas simples.

## Archivos

- `analizar_patrones.py` - Analiza el CSV original y extrae los patrones de cada empleado
- `generar_nomina_desde_patrones.py` - Genera el CSV completo a partir de los patrones identificados
- `patrones_nomina.json` - Archivo JSON con los patrones identificados
- `patrones_nomina_simplificado.csv` - Resumen de patrones en formato CSV

## Uso

### Paso 1: Analizar Patrones (solo una vez)

Ejecuta el script de análisis para extraer los patrones del CSV original:

```bash
python3 analizar_patrones.py
```

Esto generará:
- `patrones_nomina.json` - Patrones en formato JSON
- `patrones_nomina_simplificado.csv` - Resumen legible

### Paso 2: Generar Nómina

Una vez identificados los patrones, puedes generar la nómina para cualquier período:

```bash
python3 generar_nomina_desde_patrones.py
```

El script te pedirá:
- Fecha de inicio (formato: DD/MM/YY)
- Fecha de fin (formato: DD/MM/YY)

O puedes presionar Enter para usar valores por defecto.

## Patrones Identificados

Cada empleado tiene:
- **Horario fijo**: El horario de trabajo no cambia
- **Días laborales**: Días de la semana que normalmente trabaja
- **Grupo**: A o B (para rotación)
- **Trabaja festivos**: Si trabaja en días festivos
- **Trabaja domingos**: Si trabaja los domingos

### Patrón Especial de Rotación Mi-Vi

**Daniel Alfonso Lara Torres** y **Juan David Gahona Ramirez** tienen un patrón especial:
- Ambos trabajan **solo Miércoles, Jueves y Viernes**
- **Daniel (Grupo A)**: Trabaja Mi-Vi en semanas pares (según fecha de inicio)
- **Juan (Grupo B)**: Trabaja Mi-Vi en semanas impares (alternando con Daniel)
- Rotan semanalmente: cuando Daniel trabaja, Juan descansa y viceversa

## Estructura de Patrones

El archivo `patrones_nomina.json` contiene:

```json
{
  "empleados": [
    {
      "nombre": "Nombre del empleado",
      "horario": "00:00 - 09:00",
      "grupo": "A",
      "dias_laborales": [3, 4, 5],
      "dias_laborales_texto": ["Miércoles", "Jueves", "Viernes"],
      "trabaja_festivos": true,
      "trabaja_domingos": true,
      "patron_semanal": {
        "1": false,  // Lunes
        "2": false,  // Martes
        "3": true,   // Miércoles
        "4": true,   // Jueves
        "5": true,   // Viernes
        "6": false,  // Sábado
        "7": false   // Domingo
      }
    }
  ]
}
```

## Notas

- Los grupos A y B rotan semanalmente
- Los festivos y domingos se manejan según las preferencias de cada empleado
- El sistema genera automáticamente los valores (0 o 9) según los patrones

## Interfaz Web de Consulta

Se ha creado una interfaz web para consultar horarios fácilmente:

### Uso de la Interfaz

1. **Abrir la interfaz**: Abre el archivo `consulta_horarios.html` en tu navegador
   - Puedes hacer doble clic en el archivo o arrastrarlo a tu navegador
   - También puedes usar: `open consulta_horarios.html` en la terminal

2. **Seleccionar fecha**: Elige la fecha que quieres consultar usando el selector de fecha

3. **Seleccionar analistas**: 
   - Marca los analistas que quieres consultar
   - Usa "Seleccionar Todos" o "Deseleccionar Todos" para facilitar la selección

4. **Consultar**: Haz clic en "Consultar Horarios" para ver los resultados

### Características de la Interfaz

- ✅ Consulta rápida de horarios por fecha
- ✅ Múltiples analistas a la vez
- ✅ Muestra si el analista trabaja o no ese día
- ✅ Información detallada: horario, grupo, días laborales
- ✅ Indicadores visuales claros (verde = trabaja, rojo = no trabaja)
- ✅ Funciona sin conexión a internet (datos incluidos)

## Personalización

Puedes editar `patrones_nomina.json` directamente para ajustar los patrones si es necesario.

**Nota**: Si actualizas `patrones_nomina.json`, también deberás actualizar los datos en `consulta_horarios.html` (en la sección `datosAnalistas`) para que la interfaz refleje los cambios.


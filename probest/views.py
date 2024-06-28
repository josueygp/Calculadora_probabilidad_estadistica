from django.shortcuts import render
from .models import aplicacion
import pandas as pd
import random



# Create your views here.
def home(request):
    

    aplicaciones = aplicacion.objects.all()
    context = {
        'aplicaciones': aplicaciones,
    }


    return render(request,'home.html', context)


def tallo_hoja(request):
    if request.method == 'POST':
        numbers = request.POST.get('numbers')
        if numbers:
            numbers = list(map(int, numbers.split(',')))
            stem_leaf_dict = {}
            ############## Convertir la lista de números a un DataFrame de pandas
            df = pd.DataFrame(numbers, columns=['values'])
            ################ Usar la función cut para obtener tallos
            df['stem'] = df['values'] // 10
            df['leaf'] = df['values'] % 10
            ################## Agrupar por tallo y recoger hojas
            grouped = df.groupby('stem')['leaf'].apply(list).to_dict()
            ################ Ordenar las hojas dentro de cada tallo
            for key in grouped:
                grouped[key].sort()
           
            registered_numbers = sorted(numbers)

            context = {'stem_leaf_dict': grouped, 'numbers': numbers, 'registered_numbers': registered_numbers}
            return render(request, 'tallo_hoja.html', context)
        else:
            #################### Manejar el caso en el que no se proporciona una lista de números
            start_range = request.POST.get('start_range')
            end_range = request.POST.get('end_range')
            count = request.POST.get('count')
            if start_range and end_range and count:
                try:
                    start_range = int(start_range)
                    end_range = int(end_range)
                    count = int(count)
                    random_numbers = [random.randint(start_range, end_range) for _ in range(count)]
                    random_numbers_str = ', '.join(map(str, random_numbers))

                    ##############Agregar la sección de "Números registrados" para números aleatorios
                    stem_leaf_dict = {}
                    df = pd.DataFrame(random_numbers, columns=['values'])
                    df['stem'] = df['values'] // 10
                    df['leaf'] = df['values'] % 10
                    grouped = df.groupby('stem')['leaf'].apply(list).to_dict()
                    for key in grouped:
                        grouped[key].sort()

                    ################# Ordenar los números aleatorios de menor a mayor
                    registered_numbers = sorted(random_numbers)

                    context = {'stem_leaf_dict': grouped, 'random_numbers': random_numbers_str, 'registered_numbers': registered_numbers}
                    return render(request, 'tallo_hoja.html', context)
                except ValueError:
                    error_message = "Los valores de inicio del rango, fin del rango y cantidad deben ser números enteros."
            else:
                error_message = "Por favor, complete todos los campos del rango."
            context = {'error_message': error_message}
            return render(request, 'tallo_hoja.html', context)
    return render(request, 'tallo_hoja.html')


##########################################################
from django.shortcuts import render
import pandas as pd
import numpy as np

def tabla_frecuencia(request):
    if request.method == 'POST':
        numbers = request.POST.get('numbers')
        data_type = request.POST.get('data_type')
        
        if numbers:
            numbers = list(map(int, numbers.split(',')))
            # Crear un DataFrame
            df = pd.DataFrame(numbers, columns=['values'])
            
            if data_type == 'agrupados':
                # Determinar los intervalos
                min_value, max_value = df['values'].min(), df['values'].max()
                bins = np.arange(min_value, max_value + 10, 10)

                # Calcular la tabla de frecuencia para datos agrupados
                df['interval'] = pd.cut(df['values'], bins, right=False)
                frequency_table = df['interval'].value_counts().sort_index().reset_index()
                frequency_table.columns = ['interval', 'frequency']

                # Calcular frecuencias acumuladas y relativas
                frequency_table['cumulative_frequency'] = frequency_table['frequency'].cumsum()
                total = frequency_table['frequency'].sum()
                frequency_table['relative_frequency'] = frequency_table['frequency'] / total
                frequency_table['cumulative_relative_frequency'] = frequency_table['relative_frequency'].cumsum()

                # Calcular medidas de tendencia central para datos agrupados
                midpoints = [(interval.left + interval.right) / 2 for interval in frequency_table['interval']]
                frequency_table['midpoint'] = midpoints
                weighted_mean = sum(frequency_table['midpoint'] * frequency_table['frequency']) / total
                mean_value = weighted_mean

                # Calcular mediana para datos agrupados
                cumulative_freqs = frequency_table['cumulative_frequency']
                median_class = frequency_table[cumulative_freqs >= total / 2].iloc[0]
                l = median_class['interval'].left
                F = frequency_table.loc[frequency_table['interval'] == median_class['interval'], 'cumulative_frequency'].iloc[0] - median_class['frequency']
                f = median_class['frequency']
                w = median_class['interval'].right - median_class['interval'].left
                median_value = l + ((total / 2 - F) / f) * w

                # Calcular moda para datos agrupados
                mode_class = frequency_table[frequency_table['frequency'] == frequency_table['frequency'].max()].iloc[0]
                l = mode_class['interval'].left
                f1 = mode_class['frequency']
                # Obtener frecuencias de clases adyacentes
                mode_index = frequency_table.index[frequency_table['interval'] == mode_class['interval']][0]
                f0 = frequency_table['frequency'].iloc[mode_index - 1] if mode_index > 0 else 0
                f2 = frequency_table['frequency'].iloc[mode_index + 1] if mode_index < len(frequency_table) - 1 else 0
                mode_value = l + ((f1 - f0) / ((f1 - f0) + (f1 - f2))) * w

                # Calcular medidas de dispersión
                range_value = max_value - min_value
                variance_value = sum(frequency_table['frequency'] * (frequency_table['midpoint'] - mean_value) ** 2) / total
                std_dev_value = np.sqrt(variance_value)

                context = {
                    'frequency_table': frequency_table.to_dict(orient='records'),
                    'numbers': numbers,
                    'data_type': data_type,
                    'mean_value': mean_value,
                    'median_value': median_value,
                    'mode_value': mode_value,
                    'range_value': range_value,
                    'variance_value': variance_value,
                    'std_dev_value': std_dev_value
                }
                return render(request, 'tabla_frecuencia.html', context)
            else:
                # Calcular la tabla de frecuencia para datos no agrupados
                frequency_table = df['values'].value_counts().sort_index().reset_index()
                frequency_table.columns = ['value', 'frequency']

                # Calcular frecuencias acumuladas y relativas
                frequency_table['cumulative_frequency'] = frequency_table['frequency'].cumsum()
                total = frequency_table['frequency'].sum()
                frequency_table['relative_frequency'] = frequency_table['frequency'] / total
                frequency_table['cumulative_relative_frequency'] = frequency_table['relative_frequency'].cumsum()

                # Calcular medidas de tendencia central
                mean_value = df['values'].mean()
                median_value = df['values'].median()
                mode_value = df['values'].mode().tolist()

                # Calcular medidas de dispersión
                range_value = df['values'].max() - df['values'].min()
                variance_value = df['values'].var()
                std_dev_value = df['values'].std()

                context = {
                    'frequency_table': frequency_table.to_dict(orient='records'),
                    'numbers': numbers,
                    'mean_value': mean_value,
                    'median_value': median_value,
                    'mode_value': mode_value,
                    'data_type': data_type,
                    'range_value': range_value,
                    'variance_value': variance_value,
                    'std_dev_value': std_dev_value
                }
                return render(request, 'tabla_frecuencia.html', context)
        else:
            error_message = "Por favor, ingrese una lista de números separados por comas."
            context = {'error_message': error_message}
            return render(request, 'tabla_frecuencia.html', context)
    return render(request, 'tabla_frecuencia.html')

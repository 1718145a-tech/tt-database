import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# =========================================================================
# === INGRESA LAS RUTAS DE LOS ARCHIVOS Y LA CARPETA DE SALIDA AQUÍ ===
# =========================================================================
hcm_file = r"C:\Users\aijab\Documents\documentos\AJBM\MAESTRÍA\TRÁNSITO\TESIS\Archivos de tesis\Graficas_comparacion\Tiempos_CSV_HCM.csv"
maps_file = r"C:\Users\aijab\Documents\documentos\AJBM\MAESTRÍA\TRÁNSITO\TESIS\Archivos de tesis\Graficas_comparacion\Tiempos_CSV_Maps.csv"
output_dir = r"C:\Users\aijab\Documents\documentos\AJBM\MAESTRÍA\TRÁNSITO\TESIS\Archivos de tesis\Graficas_comparacion"
# =========================================================================

def load_data(file_path):
    """
    Carga los datos de un archivo CSV y devuelve las columnas 'Perf. Measure (s)'
    y 'Start Time (hr)'.
    """
    try:
        df = pd.read_csv(file_path)
        required_cols = ['Perf. Measure (s)', 'Start Time (hr)']
        if all(col in df.columns for col in required_cols):
            return df[required_cols].dropna()
        else:
            print(f"Error: No se encontraron las columnas requeridas en el archivo {file_path}")
            return None
    except FileNotFoundError:
        print(f"Error: El archivo no se encontró en la ruta: {file_path}")
        return None

def calculate_stats(data):
    """
    Calcula los estadísticos requeridos para el análisis.
    """
    data_sorted = np.sort(data)

    p50, p85, p95 = np.percentile(data_sorted, [50, 85, 95])
    free_flow_time = np.mean(data_sorted[:int(len(data) * 0.10)])
    average = np.mean(data_sorted)

    return {
        'P50': p50,
        'P85': p85,
        'P95': p95,
        'Free Flow Time': free_flow_time,
        'Average': average
    }

def generate_box_plot(data_hcm, data_maps, output_dir):
    """
    Genera y guarda el gráfico de cajas y bigotes comparando ambos archivos
    agrupados por la hora del día.
    """
    plt.style.use('seaborn-v0_8-whitegrid')

    data_hcm['Start Time (hr)'] = pd.to_numeric(data_hcm['Start Time (hr)'])
    data_maps['Start Time (hr)'] = pd.to_numeric(data_maps['Start Time (hr)'])

    hours = sorted(data_hcm['Start Time (hr)'].unique())

    fig, ax = plt.subplots(figsize=(12, 8))

    positions_hcm = np.arange(len(hours)) - 0.2
    positions_maps = np.arange(len(hours)) + 0.2

    boxplot_data_hcm = [data_hcm[data_hcm['Start Time (hr)'] == h]['Perf. Measure (s)'] for h in hours]
    boxplot_data_maps = [data_maps[data_maps['Start Time (hr)'] == h]['Perf. Measure (s)'] for h in hours]

    bp_hcm = ax.boxplot(boxplot_data_hcm, positions=positions_hcm, widths=0.3, patch_artist=True, boxprops=dict(facecolor='lightblue', color='blue'))
    bp_maps = ax.boxplot(boxplot_data_maps, positions=positions_maps, widths=0.3, patch_artist=True, boxprops=dict(facecolor='lightgreen', color='green'))

    # TEXTOS EN INGLÉS Y TAMAÑO 20
    ax.set_title('Travel Times', fontsize=20)
    ax.set_xlabel('Time of Day', fontsize=20)
    ax.set_ylabel('Travel Time (s)', fontsize=20)
    ax.set_xticks(np.arange(len(hours)))
    ax.set_xticklabels([str(h) for h in hours], fontsize=20)
    ax.tick_params(axis='both', labelsize=20)
    ax.grid(True)

    legend_elements = [plt.Rectangle((0, 0), 1, 1, fc='lightblue', ec='blue', label='HCM'),
                       plt.Rectangle((0, 0), 1, 1, fc='lightgreen', ec='green', label='Maps')]
    ax.legend(handles=legend_elements, fontsize=20)

    output_path = os.path.join(output_dir, 'boxplot_comparativo.png')
    plt.savefig(output_path, bbox_inches='tight')
    print(f"Box plot saved at: {output_path}")
    plt.close(fig)

def generate_cdf_plot(data_hcm, data_maps, stats_hcm, stats_maps, output_dir):
    """
    Genera y guarda el gráfico de la función de distribución acumulativa (CDF).
    """
    plt.style.use('seaborn-v0_8-whitegrid')

    fig, ax = plt.subplots(figsize=(12, 9))

    data_hcm_sorted = np.sort(data_hcm['Perf. Measure (s)'])
    cdf_hcm = np.arange(1, len(data_hcm_sorted) + 1) / len(data_hcm_sorted)

    data_maps_sorted = np.sort(data_maps['Perf. Measure (s)'])
    cdf_maps = np.arange(1, len(data_maps_sorted) + 1) / len(data_maps_sorted)

    ax.plot(data_hcm_sorted, cdf_hcm, label='HCM', linewidth=2, color='blue')
    ax.plot(data_maps_sorted, cdf_maps, label='Maps', linestyle='--', linewidth=2, color='orange')

    if data_hcm_sorted[-1] < 1200:
        ax.plot([data_hcm_sorted[-1], 1200], [cdf_hcm[-1], cdf_hcm[-1]], color='blue', linestyle='-')

    ax.set_xlim(250, 900)

    ax.scatter(stats_hcm['P50'], 0.50, color='blue', zorder=5)
    ax.scatter(stats_hcm['P85'], 0.85, color='blue', zorder=5)
    ax.scatter(stats_hcm['P95'], 0.95, color='blue', zorder=5)

    ax.scatter(stats_maps['P50'], 0.50, color='orange', zorder=5)
    ax.scatter(stats_maps['P85'], 0.85, color='orange', zorder=5)
    ax.scatter(stats_maps['P95'], 0.95, color='orange', zorder=5)

    ax.axhline(0.50, color='gray', linestyle=':', linewidth=0.8)
    ax.axhline(0.85, color='gray', linestyle=':', linewidth=0.8)
    ax.axhline(0.95, color='gray', linestyle=':', linewidth=0.8)

    # TEXTOS EN INGLÉS Y TAMAÑO 20
    ax.set_title('Cumulative Distribution Function (CDF)', fontsize=20)
    ax.set_xlabel('Travel Time (s)', fontsize=20)
    ax.set_ylabel('Cumulative Probability', fontsize=20)
    ax.tick_params(axis='both', labelsize=20)
    ax.grid(True)

    legend_elements = [
        plt.Line2D([0], [0], color='blue', lw=2, label='HCM'),
        plt.Line2D([0], [0], color='orange', lw=2, linestyle='--', label='Maps'),

        plt.Line2D([0], [0], color='w', label=f"__HCM__\n  P50: {stats_hcm['P50']:.1f}\n  P85: {stats_hcm['P85']:.1f}\n  P95: {stats_hcm['P95']:.1f}\n  FFT: {stats_hcm['Free Flow Time']:.1f}\n  Avg: {stats_hcm['Average']:.1f}"),

        plt.Line2D([0], [0], color='w', label=f"__Maps__\n  P50: {stats_maps['P50']:.1f}\n  P85: {stats_maps['P85']:.1f}\n  P95: {stats_maps['P95']:.1f}\n  FFT: {stats_maps['Free Flow Time']:.1f}\n  Avg: {stats_maps['Average']:.1f}")
    ]

    ax.legend(handles=legend_elements, loc='lower right', framealpha=0.8, fontsize=20)

    output_path = os.path.join(output_dir, 'cdf_comparativa.png')
    plt.savefig(output_path, bbox_inches='tight')
    print(f"CDF plot saved at: {output_path}")
    plt.close(fig)

def main():
    print("--- Travel Time Analyzer ---")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Output directory created: {output_dir}")

    print("\nLoading data...")
    data_hcm = load_data(hcm_file)
    data_maps = load_data(maps_file)

    if data_hcm is None or data_maps is None:
        return

    print("Calculating statistics...")
    stats_hcm = calculate_stats(data_hcm['Perf. Measure (s)'])
    stats_maps = calculate_stats(data_maps['Perf. Measure (s)'])

    print("\nGenerating plots...")
    generate_box_plot(data_hcm, data_maps, output_dir)
    generate_cdf_plot(data_hcm, data_maps, stats_hcm, stats_maps, output_dir)

    print("\nAnalysis completed. Check the output folder!")

if __name__ == '__main__':
    main()
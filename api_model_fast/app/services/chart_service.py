import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64
from app.utils.exceptions import ChartError


class ChartService:
    def __init__(self):
        plt.switch_backend("Agg")  # Para evitar problemas en entornos sin GUI

    def generate_chart(self, df, chart_fields):
        """
        Genera un gráfico a partir de un DataFrame y el código generado por IA
        """
        try:
            # Obtener el código del gráfico
            chart_code = chart_fields.get("chart_code")

            return self._execute_chart_code(df, chart_code, chart_fields)

        except ChartError:
            raise
        except Exception as e:
            raise ChartError(f"Error generando gráfico: {str(e)}")

    def _execute_chart_code(self, df, chart_code, chart_fields):
        """
        Ejecuta el código del gráfico de forma segura
        """
        try:
            # Preparar el namespace para la ejecución del código
            namespace = {
                "df": df,
                "plt": plt,
                "sns": sns,
                "pd": pd,
                "chart_fields": chart_fields,
            }

            # Limpiar cualquier figura previa
            plt.close("all")

            # Ejecutar el código generado
            exec(chart_code, namespace)

            # Convertir el gráfico a base64
            return self._plot_to_base64()

        except SyntaxError as e:
            raise ChartError(f"Error de sintaxis en el código del gráfico: {str(e)}")
        except KeyError as e:
            raise ChartError(f"Columna no encontrada en el DataFrame: {str(e)}")
        except Exception as e:
            raise ChartError(f"Error ejecutando código del gráfico: {str(e)}")

    def _plot_to_base64(self):
        """Convierte el gráfico a base64 para enviar via API"""
        try:
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format="png", dpi=100, bbox_inches="tight")
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
            plt.close("all")  # Cerrar todas las figuras para liberar memoria
            return img_base64
        except Exception as e:
            plt.close("all")
            raise ChartError(f"Error convirtiendo gráfico a base64: {str(e)}")


# Instancia global
chart_service = ChartService()

"""
logger_sistema.py
=================
Módulo de registro de eventos y errores (logging) para Software FJ.
Registra todos los eventos relevantes en un archivo de texto plano.

Autor: Equipo de desarrollo
Curso: Programación 213023 - UNAD
"""

import os
from datetime import datetime


class LoggerSistema:
    """
    Clase singleton responsable de registrar todos los eventos
    y errores del sistema en un archivo de logs.

    Utiliza el patrón Singleton para garantizar una única instancia
    de logger durante la ejecución del programa.
    """

    _instancia = None
    ARCHIVO_LOG = "software_fj_eventos.log"

    def __new__(cls):
        """Implementación del patrón Singleton."""
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        """Inicializa el logger y crea la cabecera del archivo de log."""
        self._ruta_log = self.ARCHIVO_LOG
        self._escribir_cabecera()

    def _obtener_timestamp(self) -> str:
        """Retorna la marca de tiempo actual formateada."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _escribir_cabecera(self):
        """Escribe la cabecera del archivo de log al iniciar el sistema."""
        try:
            with open(self._ruta_log, "a", encoding="utf-8") as f:
                f.write("\n" + "=" * 70 + "\n")
                f.write(f"  SOFTWARE FJ - Sistema de Gestión\n")
                f.write(f"  Sesión iniciada: {self._obtener_timestamp()}\n")
                f.write("=" * 70 + "\n")
        except OSError as e:
            print(f"[ADVERTENCIA] No se pudo inicializar el archivo de log: {e}")

    def _registrar(self, nivel: str, mensaje: str):
        """
        Método interno que escribe una entrada en el archivo de log.

        Args:
            nivel: Nivel del evento (INFO, ERROR, ADVERTENCIA, etc.)
            mensaje: Descripción del evento a registrar.
        """
        entrada = f"[{self._obtener_timestamp()}] [{nivel:12}] {mensaje}\n"
        try:
            with open(self._ruta_log, "a", encoding="utf-8") as f:
                f.write(entrada)
        except OSError as e:
            # Si no se puede escribir en el log, se imprime en consola como respaldo
            print(f"[LOG-ERROR] No se pudo escribir en el log: {e}")
        finally:
            # Siempre mostramos el evento en consola para seguimiento en tiempo real
            print(entrada.strip())

    def info(self, mensaje: str):
        """Registra un evento informativo exitoso."""
        self._registrar("INFO", mensaje)

    def error(self, mensaje: str):
        """Registra un evento de error."""
        self._registrar("ERROR", mensaje)

    def advertencia(self, mensaje: str):
        """Registra una advertencia del sistema."""
        self._registrar("ADVERTENCIA", mensaje)

    def exito(self, mensaje: str):
        """Registra una operación exitosa."""
        self._registrar("ÉXITO", mensaje)

    def seccion(self, titulo: str):
        """Registra un separador de sección para mayor legibilidad del log."""
        separador = f"\n{'─' * 60}\n  {titulo}\n{'─' * 60}"
        try:
            with open(self._ruta_log, "a", encoding="utf-8") as f:
                f.write(separador + "\n")
        except OSError:
            pass
        print(separador)

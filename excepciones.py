"""
excepciones.py
==============
Módulo de excepciones personalizadas para el Sistema de Gestión
de Clientes, Servicios y Reservas - Software FJ.

Autor: Equipo de desarrollo
Curso: Programación 213023 - UNAD
"""


class SistemaFJError(Exception):
    """
    Excepción base del sistema Software FJ.
    Todas las excepciones personalizadas heredan de esta clase.
    """
    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(f"[{codigo}] {mensaje}")

    def __str__(self):
        return f"[{self.codigo}] {self.mensaje}"


class ClienteInvalidoError(SistemaFJError):
    """
    Se lanza cuando los datos de un cliente son inválidos o incompletos.
    Ejemplos: nombre vacío, email sin formato correcto, teléfono inválido.
    """
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CLIENTE")


class ServicioNoDisponibleError(SistemaFJError):
    """
    Se lanza cuando un servicio solicitado no está disponible o activo.
    """
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_SERVICIO")


class ReservaInvalidaError(SistemaFJError):
    """
    Se lanza cuando una reserva no puede procesarse por datos inválidos
    o condiciones no satisfechas.
    """
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_RESERVA")


class DuracionInvalidaError(SistemaFJError):
    """
    Se lanza cuando la duración especificada para un servicio es inválida
    (negativa, cero, o fuera del rango permitido).
    """
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_DURACION")


class CapacidadExcedidaError(SistemaFJError):
    """
    Se lanza cuando se intenta reservar un recurso que supera su capacidad
    máxima permitida (ej: sala con aforo excedido).
    """
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CAPACIDAD")


class ParametroFaltanteError(SistemaFJError):
    """
    Se lanza cuando faltan parámetros obligatorios para una operación.
    """
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_PARAMETRO")


class OperacionNoPermitidaError(SistemaFJError):
    """
    Se lanza cuando se intenta realizar una operación no permitida,
    como cancelar una reserva ya finalizada.
    """
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_OPERACION")


class CalculoCostoError(SistemaFJError):
    """
    Se lanza cuando ocurre un error durante el cálculo del costo
    de un servicio (descuentos inválidos, impuestos incorrectos, etc.).
    """
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_COSTO")


class ClienteNoEncontradoError(SistemaFJError):
    """
    Se lanza cuando no se encuentra un cliente en el sistema.
    """
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CLIENTE_NF")


class ServicioNoEncontradoError(SistemaFJError):
    """
    Se lanza cuando no se encuentra un servicio en el sistema.
    """
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_SERVICIO_NF")

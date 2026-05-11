"""
servicios.py
============
Módulo que define la clase abstracta Servicio y los tres servicios
especializados de Software FJ:
  - ReservaSala:          Alquiler de salas de reuniones.
  - AlquilerEquipo:       Alquiler de equipos tecnológicos.
  - AsesoriaEspecializada: Sesiones de consultoría con expertos.

Autor: Equipo de desarrollo
Curso: Programación 213023 - UNAD
"""

from abc import abstractmethod
from entidad import Entidad
from excepciones import (
    ServicioNoDisponibleError,
    DuracionInvalidaError,
    CapacidadExcedidaError,
    CalculoCostoError,
    ParametroFaltanteError,
)


# ════════════════════════════════════════════════════════════════════════════
# CLASE ABSTRACTA BASE: Servicio
# ════════════════════════════════════════════════════════════════════════════

class Servicio(Entidad):
    """
    Clase abstracta que define la interfaz común para todos los servicios
    ofrecidos por Software FJ.

    Principios OOP aplicados:
    - Abstracción: métodos abstractos calcular_costo() y describir_servicio()
    - Encapsulación: precio base y disponibilidad son atributos privados.
    - Herencia: hereda de Entidad (clase abstracta raíz).
    - Polimorfismo: calcular_costo() se comporta diferente en cada subclase.
    """

    # Impuesto por defecto aplicable a todos los servicios (IVA)
    IVA_DEFAULT = 0.19  # 19%

    def __init__(self, nombre: str, precio_base_hora: float, descripcion: str = ""):
        """
        Args:
            nombre:            Nombre del servicio.
            precio_base_hora:  Precio por hora en pesos colombianos.
            descripcion:       Descripción breve del servicio.

        Raises:
            ParametroFaltanteError: Si nombre está vacío.
            ServicioNoDisponibleError: Si el precio es inválido.
        """
        if precio_base_hora is None:
            raise ParametroFaltanteError("El precio base del servicio es obligatorio.")
        if precio_base_hora <= 0:
            raise ServicioNoDisponibleError(
                f"El precio base debe ser mayor a cero. Recibido: {precio_base_hora}"
            )

        super().__init__(nombre)
        self.__precio_base_hora = float(precio_base_hora)
        self.__descripcion = descripcion.strip() if descripcion else "Sin descripción."
        self.__disponible = True

    # ── Propiedades ─────────────────────────────────────────────────────────

    @property
    def precio_base_hora(self) -> float:
        return self.__precio_base_hora

    @precio_base_hora.setter
    def precio_base_hora(self, valor: float):
        if valor <= 0:
            raise ServicioNoDisponibleError(f"Precio inválido: {valor}")
        self.__precio_base_hora = float(valor)

    @property
    def descripcion(self) -> str:
        return self.__descripcion

    @property
    def disponible(self) -> bool:
        return self.__disponible

    def activar(self):
        """Activa el servicio para que pueda ser reservado."""
        self.__disponible = True

    def desactivar(self):
        """Desactiva el servicio (no podrá ser reservado)."""
        self.__disponible = False

    def verificar_disponibilidad(self):
        """
        Lanza excepción si el servicio no está disponible.

        Raises:
            ServicioNoDisponibleError: Si el servicio está inactivo.
        """
        if not self.__disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' no está disponible actualmente."
            )

    # ── Métodos abstractos (polimorfismo) ────────────────────────────────────

    @abstractmethod
    def calcular_costo(self, horas: float, **kwargs) -> float:
        """
        Calcula el costo total del servicio para la duración indicada.
        Cada subclase implementa su propio algoritmo de cálculo.

        Args:
            horas:  Duración en horas.
            kwargs: Parámetros opcionales (descuento, con_iva, etc.)

        Returns:
            Costo total calculado.
        """
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Retorna una descripción técnica y detallada del servicio."""
        pass

    @abstractmethod
    def validar_parametros(self, horas: float, **kwargs) -> bool:
        """
        Valida los parámetros específicos antes de procesar la reserva.
        Retorna True si los parámetros son válidos.
        """
        pass

    # ── Método sobrecargado: calcular_costo_con_opciones ────────────────────
    # Python no soporta sobrecarga directa, se usa *args/**kwargs para simularla

    def calcular_costo_con_opciones(
        self,
        horas: float,
        con_iva: bool = True,
        descuento: float = 0.0,
        cargo_extra: float = 0.0
    ) -> dict:
        """
        Versión extendida del cálculo de costo con opciones completas.
        Simula sobrecarga de métodos mediante parámetros opcionales.

        Args:
            horas:       Duración en horas.
            con_iva:     Si se aplica IVA (default: True).
            descuento:   Porcentaje de descuento 0-100 (default: 0).
            cargo_extra: Cargo adicional fijo en pesos (default: 0).

        Returns:
            Diccionario con desglose completo del costo.

        Raises:
            CalculoCostoError: Si los parámetros de cálculo son inválidos.
            DuracionInvalidaError: Si las horas son inválidas.
        """
        try:
            if horas <= 0:
                raise DuracionInvalidaError(
                    f"Las horas deben ser positivas. Recibido: {horas}"
                )
            if not (0 <= descuento <= 100):
                raise CalculoCostoError(
                    f"El descuento debe estar entre 0 y 100%. Recibido: {descuento}%"
                )
            if cargo_extra < 0:
                raise CalculoCostoError(
                    f"El cargo extra no puede ser negativo. Recibido: {cargo_extra}"
                )

            subtotal = self.calcular_costo(horas)
            valor_descuento = subtotal * (descuento / 100)
            subtotal_con_descuento = subtotal - valor_descuento
            valor_iva = subtotal_con_descuento * self.IVA_DEFAULT if con_iva else 0.0
            total = subtotal_con_descuento + valor_iva + cargo_extra

            return {
                "servicio": self.nombre,
                "horas": horas,
                "subtotal": round(subtotal, 2),
                "descuento_pct": descuento,
                "valor_descuento": round(valor_descuento, 2),
                "iva_pct": self.IVA_DEFAULT * 100 if con_iva else 0,
                "valor_iva": round(valor_iva, 2),
                "cargo_extra": round(cargo_extra, 2),
                "total": round(total, 2)
            }

        except (DuracionInvalidaError, CalculoCostoError):
            raise
        except Exception as e:
            raise CalculoCostoError(
                f"Error inesperado al calcular el costo: {e}"
            ) from e

    # ── Implementación de métodos de Entidad ─────────────────────────────────

    def describir(self) -> str:
        """Descripción general del servicio (requerida por Entidad)."""
        estado = "Disponible ✓" if self.__disponible else "No disponible ✗"
        return (
            f"Servicio #{self.id}: {self.nombre} | "
            f"Precio/hora: ${self.__precio_base_hora:,.0f} COP | "
            f"Estado: {estado}"
        )

    def validar(self) -> bool:
        """Valida que el servicio tenga datos básicos correctos."""
        return bool(self.nombre) and self.__precio_base_hora > 0

    def __str__(self) -> str:
        return f"Servicio[{self.id}]: {self.nombre} (${self.__precio_base_hora:,.0f}/h)"


# ════════════════════════════════════════════════════════════════════════════
# SERVICIO 1: ReservaSala
# ════════════════════════════════════════════════════════════════════════════

class ReservaSala(Servicio):
    """
    Servicio de alquiler de salas de reuniones o conferencias.

    Incluye gestión de capacidad, equipamiento incluido
    y tarifas diferenciadas por número de asistentes.
    """

    CAPACIDAD_MINIMA = 2
    CAPACIDAD_MAXIMA = 50
    PRECIO_BASE_POR_HORA = 80_000  # COP

    def __init__(
        self,
        nombre: str,
        capacidad_maxima: int,
        tiene_proyector: bool = True,
        tiene_videoconferencia: bool = False
    ):
        """
        Args:
            nombre:                 Nombre de la sala (ej: "Sala Orion A").
            capacidad_maxima:       Número máximo de personas permitidas.
            tiene_proyector:        Si la sala cuenta con proyector.
            tiene_videoconferencia: Si la sala tiene sistema de videoconferencia.

        Raises:
            CapacidadExcedidaError: Si la capacidad está fuera del rango permitido.
        """
        if not isinstance(capacidad_maxima, int) or capacidad_maxima < self.CAPACIDAD_MINIMA:
            raise CapacidadExcedidaError(
                f"Capacidad inválida: {capacidad_maxima}. "
                f"Mínimo permitido: {self.CAPACIDAD_MINIMA} personas."
            )
        if capacidad_maxima > self.CAPACIDAD_MAXIMA:
            raise CapacidadExcedidaError(
                f"Capacidad {capacidad_maxima} excede el máximo de {self.CAPACIDAD_MAXIMA} personas."
            )

        # Precio ajustado según equipamiento de la sala
        precio = self.PRECIO_BASE_POR_HORA
        if tiene_videoconferencia:
            precio += 30_000  # Cargo adicional por videoconferencia
        if tiene_proyector:
            precio += 10_000  # Cargo adicional por proyector

        super().__init__(nombre, precio, f"Sala de reuniones con cap. {capacidad_maxima} personas")

        self.__capacidad_maxima = capacidad_maxima
        self.__tiene_proyector = tiene_proyector
        self.__tiene_videoconferencia = tiene_videoconferencia

    @property
    def capacidad_maxima(self) -> int:
        return self.__capacidad_maxima

    def calcular_costo(self, horas: float, **kwargs) -> float:
        """
        Calcula el costo de la sala.
        Aplica un recargo del 20% si se usa en horario nocturno (kwargs: nocturno=True).

        Args:
            horas:          Duración en horas.
            kwargs:
              - asistentes (int): Número de asistentes (valida capacidad).
              - nocturno (bool):  Si es horario nocturno (aplica recargo 20%).
        """
        self.validar_parametros(horas, **kwargs)

        costo = self.precio_base_hora * horas
        if kwargs.get("nocturno", False):
            costo *= 1.20  # Recargo nocturno del 20%
        return round(costo, 2)

    def describir_servicio(self) -> str:
        equipamiento = []
        if self.__tiene_proyector:
            equipamiento.append("Proyector HD")
        if self.__tiene_videoconferencia:
            equipamiento.append("Videoconferencia")
        eq_str = ", ".join(equipamiento) if equipamiento else "Básico"
        return (
            f"┌─ RESERVA DE SALA ──────────────────────────────────\n"
            f"│  Sala:         {self.nombre}\n"
            f"│  Capacidad:    {self.__capacidad_maxima} personas\n"
            f"│  Equipamiento: {eq_str}\n"
            f"│  Precio/hora:  ${self.precio_base_hora:,.0f} COP\n"
            f"│  Disponible:   {'Sí ✓' if self.disponible else 'No ✗'}\n"
            f"└────────────────────────────────────────────────────"
        )

    def validar_parametros(self, horas: float, **kwargs) -> bool:
        """
        Valida duración y capacidad de asistentes.

        Raises:
            DuracionInvalidaError: Si las horas son inválidas (< 1 o > 12).
            CapacidadExcedidaError: Si asistentes supera la capacidad de la sala.
        """
        if horas is None:
            raise DuracionInvalidaError("Debe especificar la duración en horas.")
        if horas < 1:
            raise DuracionInvalidaError(
                f"La duración mínima de una sala es 1 hora. Recibido: {horas}h"
            )
        if horas > 12:
            raise DuracionInvalidaError(
                f"La duración máxima por reserva es 12 horas. Recibido: {horas}h"
            )
        asistentes = kwargs.get("asistentes", 1)
        if asistentes > self.__capacidad_maxima:
            raise CapacidadExcedidaError(
                f"La sala '{self.nombre}' tiene capacidad para {self.__capacidad_maxima} "
                f"personas, pero se solicitaron {asistentes} asistentes."
            )
        return True


# ════════════════════════════════════════════════════════════════════════════
# SERVICIO 2: AlquilerEquipo
# ════════════════════════════════════════════════════════════════════════════

class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos (laptops, proyectores,
    cámaras, micrófonos, etc.).

    Permite alquilar múltiples unidades y aplica descuento por volumen.
    """

    TIPOS_VALIDOS = {"laptop", "proyector", "camara", "microfono", "tablet", "servidor"}
    PRECIO_BASE_POR_HORA = 25_000  # COP por equipo/hora

    def __init__(self, nombre: str, tipo_equipo: str, cantidad_disponible: int):
        """
        Args:
            nombre:               Nombre descriptivo del equipo.
            tipo_equipo:          Tipo de equipo (debe estar en TIPOS_VALIDOS).
            cantidad_disponible:  Unidades disponibles para alquiler.

        Raises:
            ServicioNoDisponibleError: Si el tipo de equipo no es válido.
            ParametroFaltanteError:    Si la cantidad es 0 o negativa.
        """
        tipo_lower = tipo_equipo.strip().lower() if tipo_equipo else ""
        if tipo_lower not in self.TIPOS_VALIDOS:
            raise ServicioNoDisponibleError(
                f"Tipo de equipo '{tipo_equipo}' no reconocido. "
                f"Tipos válidos: {', '.join(sorted(self.TIPOS_VALIDOS))}"
            )
        if not isinstance(cantidad_disponible, int) or cantidad_disponible <= 0:
            raise ParametroFaltanteError(
                f"La cantidad disponible debe ser un entero positivo. "
                f"Recibido: {cantidad_disponible}"
            )

        # Precio varía según tipo de equipo
        precios = {
            "laptop": 35_000,
            "proyector": 40_000,
            "camara": 50_000,
            "microfono": 15_000,
            "tablet": 25_000,
            "servidor": 80_000
        }

        super().__init__(
            nombre,
            precios.get(tipo_lower, self.PRECIO_BASE_POR_HORA),
            f"Alquiler de {tipo_lower} - {nombre}"
        )

        self.__tipo_equipo = tipo_lower
        self.__cantidad_disponible = cantidad_disponible

    @property
    def tipo_equipo(self) -> str:
        return self.__tipo_equipo

    @property
    def cantidad_disponible(self) -> int:
        return self.__cantidad_disponible

    def calcular_costo(self, horas: float, **kwargs) -> float:
        """
        Calcula el costo de alquiler.
        Aplica descuento por volumen si se alquilan más de 3 unidades.

        Args:
            horas:  Duración en horas.
            kwargs:
              - cantidad (int): Número de unidades a alquilar (default: 1).
        """
        self.validar_parametros(horas, **kwargs)

        cantidad = kwargs.get("cantidad", 1)
        costo_base = self.precio_base_hora * horas * cantidad

        # Descuento por volumen: 10% si se alquilan más de 3 unidades
        if cantidad > 3:
            costo_base *= 0.90

        return round(costo_base, 2)

    def describir_servicio(self) -> str:
        return (
            f"┌─ ALQUILER DE EQUIPO ───────────────────────────────\n"
            f"│  Equipo:       {self.nombre}\n"
            f"│  Tipo:         {self.__tipo_equipo.capitalize()}\n"
            f"│  Disponibles:  {self.__cantidad_disponible} unidad(es)\n"
            f"│  Precio/hora:  ${self.precio_base_hora:,.0f} COP por unidad\n"
            f"│  Descuento:    10% al alquilar más de 3 unidades\n"
            f"│  Disponible:   {'Sí ✓' if self.disponible else 'No ✗'}\n"
            f"└────────────────────────────────────────────────────"
        )

    def validar_parametros(self, horas: float, **kwargs) -> bool:
        """
        Valida duración y cantidad solicitada de equipos.

        Raises:
            DuracionInvalidaError:     Si horas < 1 o > 72.
            CapacidadExcedidaError:    Si la cantidad supera el stock disponible.
        """
        if horas is None or horas <= 0:
            raise DuracionInvalidaError(
                f"Duración inválida: {horas}. Debe ser mayor a 0."
            )
        if horas > 72:
            raise DuracionInvalidaError(
                f"El alquiler máximo es de 72 horas. Recibido: {horas}h"
            )
        cantidad = kwargs.get("cantidad", 1)
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ParametroFaltanteError(
                f"La cantidad debe ser un entero positivo. Recibido: {cantidad}"
            )
        if cantidad > self.__cantidad_disponible:
            raise CapacidadExcedidaError(
                f"Solo hay {self.__cantidad_disponible} unidad(es) disponibles "
                f"de '{self.nombre}'. Se solicitaron: {cantidad}"
            )
        return True


# ════════════════════════════════════════════════════════════════════════════
# SERVICIO 3: AsesoriaEspecializada
# ════════════════════════════════════════════════════════════════════════════

class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría o consultoría especializada con expertos
    en diferentes áreas tecnológicas y de negocios.

    La tarifa depende del nivel del asesor y del área de especialización.
    """

    NIVELES_VALIDOS = {"junior": 1, "senior": 2, "experto": 3, "principal": 4}
    AREAS_VALIDAS = {
        "desarrollo_software", "arquitectura", "ciberseguridad",
        "inteligencia_artificial", "gestion_proyectos", "infraestructura"
    }
    PRECIO_BASE_POR_HORA = 120_000  # COP

    def __init__(
        self,
        nombre: str,
        area_especializacion: str,
        nivel_asesor: str,
        nombre_asesor: str
    ):
        """
        Args:
            nombre:               Nombre descriptivo del servicio de asesoría.
            area_especializacion: Área técnica de la asesoría.
            nivel_asesor:         Nivel del asesor (junior/senior/experto/principal).
            nombre_asesor:        Nombre del asesor asignado.

        Raises:
            ServicioNoDisponibleError: Si el área o nivel no son válidos.
            ParametroFaltanteError:    Si el nombre del asesor está vacío.
        """
        area_lower = area_especializacion.strip().lower() if area_especializacion else ""
        if area_lower not in self.AREAS_VALIDAS:
            raise ServicioNoDisponibleError(
                f"Área '{area_especializacion}' no válida. "
                f"Áreas disponibles: {', '.join(sorted(self.AREAS_VALIDAS))}"
            )

        nivel_lower = nivel_asesor.strip().lower() if nivel_asesor else ""
        if nivel_lower not in self.NIVELES_VALIDOS:
            raise ServicioNoDisponibleError(
                f"Nivel '{nivel_asesor}' no válido. "
                f"Niveles: {', '.join(self.NIVELES_VALIDOS.keys())}"
            )

        if not nombre_asesor or not nombre_asesor.strip():
            raise ParametroFaltanteError("El nombre del asesor es obligatorio.")

        # Precio ajustado según nivel del asesor
        multiplicador = self.NIVELES_VALIDOS[nivel_lower]
        precio = self.PRECIO_BASE_POR_HORA * multiplicador

        super().__init__(
            nombre,
            precio,
            f"Asesoría en {area_lower} - Nivel {nivel_lower}"
        )

        self.__area = area_lower
        self.__nivel = nivel_lower
        self.__nombre_asesor = nombre_asesor.strip()

    @property
    def area_especializacion(self) -> str:
        return self.__area

    @property
    def nivel_asesor(self) -> str:
        return self.__nivel

    @property
    def nombre_asesor(self) -> str:
        return self.__nombre_asesor

    def calcular_costo(self, horas: float, **kwargs) -> float:
        """
        Calcula el costo de la asesoría.
        Aplica un descuento del 15% si se contratan más de 4 horas seguidas.

        Args:
            horas:  Duración de la sesión en horas.
            kwargs:
              - urgente (bool): Si es asesoría urgente, aplica recargo del 30%.
        """
        self.validar_parametros(horas, **kwargs)

        costo = self.precio_base_hora * horas

        # Descuento por sesión larga (más de 4 horas)
        if horas > 4:
            costo *= 0.85  # 15% de descuento

        # Recargo por urgencia
        if kwargs.get("urgente", False):
            costo *= 1.30

        return round(costo, 2)

    def describir_servicio(self) -> str:
        return (
            f"┌─ ASESORÍA ESPECIALIZADA ───────────────────────────\n"
            f"│  Servicio:     {self.nombre}\n"
            f"│  Área:         {self.__area.replace('_', ' ').title()}\n"
            f"│  Asesor:       {self.__nombre_asesor}\n"
            f"│  Nivel:        {self.__nivel.capitalize()}\n"
            f"│  Precio/hora:  ${self.precio_base_hora:,.0f} COP\n"
            f"│  Descuento:    15% para sesiones > 4 horas\n"
            f"│  Disponible:   {'Sí ✓' if self.disponible else 'No ✗'}\n"
            f"└────────────────────────────────────────────────────"
        )

    def validar_parametros(self, horas: float, **kwargs) -> bool:
        """
        Valida la duración de la asesoría.

        Raises:
            DuracionInvalidaError: Si horas < 0.5 o > 8.
        """
        if horas is None:
            raise DuracionInvalidaError("Debe especificar la duración de la asesoría.")
        if horas < 0.5:
            raise DuracionInvalidaError(
                f"La asesoría mínima es de 30 minutos (0.5h). Recibido: {horas}h"
            )
        if horas > 8:
            raise DuracionInvalidaError(
                f"La asesoría máxima es de 8 horas por sesión. Recibido: {horas}h"
            )
        return True

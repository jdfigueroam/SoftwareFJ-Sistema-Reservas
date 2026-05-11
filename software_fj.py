"""
╔══════════════════════════════════════════════════════════════════════════╗
║         SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ                       ║
║         Universidad Nacional Abierta y a Distancia (UNAD)               ║
║         Curso: Programación - Código: 213023                            ║
║         Ingeniería de Sistemas - ECBTI                                  ║
╚══════════════════════════════════════════════════════════════════════════╝

Descripción:
    Sistema orientado a objetos para gestionar clientes, servicios y reservas
    de la empresa Software FJ. Incluye:
      - Clases abstractas (Entidad, Servicio)
      - Herencia y polimorfismo (ReservaSala, AlquilerEquipo, AsesoriaEspecializada)
      - Encapsulación completa con propiedades
      - Excepciones personalizadas
      - Manejo de bloques try/except, try/except/else, try/except/finally
      - Encadenamiento de excepciones (raise ... from ...)
      - Sistema de logs en archivo
      - Simulación de 10+ operaciones válidas e inválidas
"""

import re
import os
from abc import ABC, abstractmethod
from datetime import datetime


# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1: EXCEPCIONES PERSONALIZADAS
# ════════════════════════════════════════════════════════════════════════════

class SistemaFJError(Exception):
    """Excepción base del sistema Software FJ."""
    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(f"[{codigo}] {mensaje}")

    def __str__(self):
        return f"[{self.codigo}] {self.mensaje}"


class ClienteInvalidoError(SistemaFJError):
    """Datos de cliente inválidos o incompletos."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CLIENTE")


class ServicioNoDisponibleError(SistemaFJError):
    """Servicio no disponible o con parámetros incorrectos."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_SERVICIO")


class ReservaInvalidaError(SistemaFJError):
    """Reserva no puede procesarse por condiciones no satisfechas."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_RESERVA")


class DuracionInvalidaError(SistemaFJError):
    """Duración especificada fuera del rango permitido."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_DURACION")


class CapacidadExcedidaError(SistemaFJError):
    """Recurso solicitado supera la capacidad máxima."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CAPACIDAD")


class ParametroFaltanteError(SistemaFJError):
    """Faltan parámetros obligatorios para la operación."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_PARAMETRO")


class OperacionNoPermitidaError(SistemaFJError):
    """Operación no permitida en el estado actual del objeto."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_OPERACION")


class CalculoCostoError(SistemaFJError):
    """Error durante el cálculo del costo de un servicio."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_COSTO")


# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2: LOGGER DEL SISTEMA
# ════════════════════════════════════════════════════════════════════════════

class LoggerSistema:
    """
    Clase Singleton para registrar eventos y errores en archivo de log.
    Garantiza una única instancia durante toda la ejecución.
    """
    _instancia = None
    ARCHIVO_LOG = "software_fj_eventos.log"

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        self._ruta_log = self.ARCHIVO_LOG
        self._escribir_cabecera()

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _escribir_cabecera(self):
        try:
            with open(self._ruta_log, "a", encoding="utf-8") as f:
                f.write("\n" + "=" * 70 + "\n")
                f.write(f"  SOFTWARE FJ - Sistema de Gestión\n")
                f.write(f"  Sesión iniciada: {self._timestamp()}\n")
                f.write("=" * 70 + "\n")
        except OSError as e:
            print(f"[ADVERTENCIA] No se pudo inicializar el log: {e}")

    def _registrar(self, nivel: str, mensaje: str):
        entrada = f"[{self._timestamp()}] [{nivel:12}] {mensaje}\n"
        try:
            with open(self._ruta_log, "a", encoding="utf-8") as f:
                f.write(entrada)
        except OSError as e:
            print(f"[LOG-FALLO] No se pudo escribir en log: {e}")
        finally:
            # Siempre se imprime en consola como respaldo
            print(entrada.strip())

    def info(self, mensaje: str):
        self._registrar("INFO", mensaje)

    def error(self, mensaje: str):
        self._registrar("ERROR", mensaje)

    def exito(self, mensaje: str):
        self._registrar("ÉXITO", mensaje)

    def advertencia(self, mensaje: str):
        self._registrar("ADVERTENCIA", mensaje)

    def seccion(self, titulo: str):
        sep = f"\n{'─' * 70}\n  {titulo}\n{'─' * 70}"
        try:
            with open(self._ruta_log, "a", encoding="utf-8") as f:
                f.write(sep + "\n")
        except OSError:
            pass
        print(sep)


# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3: CLASE ABSTRACTA BASE - Entidad
# ════════════════════════════════════════════════════════════════════════════

class Entidad(ABC):
    """
    Clase abstracta raíz del sistema.
    Toda entidad (Cliente, Servicio, Reserva) hereda de aquí.

    Principios OOP:
    - Abstracción: define contrato común sin implementación concreta.
    - Encapsulación: ID y fecha de creación son privados y de solo lectura.
    """
    _contador_global: int = 0

    def __init__(self, nombre: str):
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de la entidad no puede estar vacío.")
        Entidad._contador_global += 1
        self.__id = Entidad._contador_global
        self.__nombre = nombre.strip()
        self.__fecha_creacion = datetime.now()

    @property
    def id(self) -> int:
        return self.__id

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self.__nombre = valor.strip()

    @property
    def fecha_creacion(self) -> datetime:
        return self.__fecha_creacion

    @abstractmethod
    def describir(self) -> str:
        """Descripción detallada de la entidad (polimorfismo)."""
        pass

    @abstractmethod
    def validar(self) -> bool:
        """Valida la consistencia de los datos de la entidad."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.__id}, nombre='{self.__nombre}')"

    def __eq__(self, otro) -> bool:
        if not isinstance(otro, Entidad):
            return NotImplemented
        return self.__id == otro.id

    def __hash__(self) -> int:
        return hash(self.__id)


# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4: CLASE Cliente
# ════════════════════════════════════════════════════════════════════════════

class Cliente(Entidad):
    """
    Representa a un cliente de Software FJ.

    Implementa encapsulación completa con validaciones estrictas:
    - Email con formato válido (regex).
    - Teléfono con 7-15 dígitos numéricos.
    - Estado activo/inactivo para control de reservas.

    Hereda de: Entidad
    """

    _REGEX_EMAIL    = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
    _REGEX_TELEFONO = re.compile(r'^\+?[0-9]{7,15}$')

    def __init__(self, nombre: str, email: str, telefono: str, empresa: str = ""):
        """
        Args:
            nombre:    Nombre completo del cliente.
            email:     Correo electrónico válido.
            telefono:  Número de teléfono (7-15 dígitos).
            empresa:   Empresa del cliente (opcional).

        Raises:
            ParametroFaltanteError: Si algún campo obligatorio está vacío.
            ClienteInvalidoError:   Si email o teléfono tienen formato inválido.
        """
        # Validar parámetros antes de llamar al padre
        for campo, valor in {"nombre": nombre, "email": email, "telefono": telefono}.items():
            if not valor or not str(valor).strip():
                raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio.")

        try:
            super().__init__(nombre)
        except ValueError as e:
            raise ClienteInvalidoError(f"Nombre inválido: {e}") from e

        # Uso de setters para aplicar validaciones
        self.email    = email
        self.telefono = telefono
        self.__empresa             = empresa.strip() if empresa else "Particular"
        self.__activo              = True
        self.__historial_reservas  = []

    # ── Propiedades ─────────────────────────────────────────────────────────

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor: str):
        if not valor or not valor.strip():
            raise ParametroFaltanteError("El email es obligatorio.")
        valor = valor.strip().lower()
        if not self._REGEX_EMAIL.match(valor):
            raise ClienteInvalidoError(
                f"Email '{valor}' inválido. Formato esperado: usuario@dominio.com"
            )
        self.__email = valor

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not str(valor).strip():
            raise ParametroFaltanteError("El teléfono es obligatorio.")
        valor = str(valor).strip().replace(" ", "").replace("-", "")
        if not self._REGEX_TELEFONO.match(valor):
            raise ClienteInvalidoError(
                f"Teléfono '{valor}' inválido. Debe tener entre 7 y 15 dígitos."
            )
        self.__telefono = valor

    @property
    def empresa(self) -> str:
        return self.__empresa

    @property
    def activo(self) -> bool:
        return self.__activo

    @property
    def historial_reservas(self) -> list:
        return list(self.__historial_reservas)  # Copia protegida

    # ── Métodos públicos ─────────────────────────────────────────────────────

    def agregar_reserva(self, id_reserva: int):
        if not self.__activo:
            raise ClienteInvalidoError(
                f"Cliente '{self.nombre}' está inactivo; no puede registrar reservas."
            )
        if id_reserva not in self.__historial_reservas:
            self.__historial_reservas.append(id_reserva)

    def desactivar(self):
        self.__activo = False

    def activar(self):
        self.__activo = True

    def total_reservas(self) -> int:
        return len(self.__historial_reservas)

    # ── Métodos abstractos implementados ────────────────────────────────────

    def describir(self) -> str:
        estado = "Activo ✓" if self.__activo else "Inactivo ✗"
        return (
            f"\n┌─ CLIENTE #{self.id} {'─' * 45}\n"
            f"│  Nombre:     {self.nombre}\n"
            f"│  Email:      {self.__email}\n"
            f"│  Teléfono:   {self.__telefono}\n"
            f"│  Empresa:    {self.__empresa}\n"
            f"│  Estado:     {estado}\n"
            f"│  Reservas:   {self.total_reservas()}\n"
            f"│  Registrado: {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}\n"
            f"└{'─' * 58}"
        )

    def validar(self) -> bool:
        try:
            return (
                bool(self.nombre)
                and bool(self.__email)
                and bool(self.__telefono)
                and self._REGEX_EMAIL.match(self.__email) is not None
                and self._REGEX_TELEFONO.match(self.__telefono) is not None
            )
        except Exception:
            return False

    def __str__(self) -> str:
        return f"Cliente[{self.id}]: {self.nombre} ({self.__email})"


# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5: CLASE ABSTRACTA Servicio + 3 SERVICIOS ESPECIALIZADOS
# ════════════════════════════════════════════════════════════════════════════

class Servicio(Entidad):
    """
    Clase abstracta que define la interfaz común para todos los servicios.

    Principios OOP:
    - Abstracción: calcular_costo(), describir_servicio(), validar_parametros()
      son abstractos y cada subclase los implementa diferente (polimorfismo).
    - Encapsulación: precio base y disponibilidad son privados.
    - Métodos sobrecargados: calcular_costo_con_opciones() simula sobrecarga
      mediante parámetros opcionales (Python no tiene sobrecarga nativa).
    """

    IVA = 0.19  # 19% IVA colombiano

    def __init__(self, nombre: str, precio_base_hora: float, descripcion: str = ""):
        if precio_base_hora is None:
            raise ParametroFaltanteError("El precio base del servicio es obligatorio.")
        if precio_base_hora <= 0:
            raise ServicioNoDisponibleError(
                f"El precio base debe ser mayor a cero. Recibido: {precio_base_hora}"
            )
        super().__init__(nombre)
        self.__precio_base_hora = float(precio_base_hora)
        self.__descripcion      = descripcion.strip() if descripcion else "Sin descripción."
        self.__disponible       = True

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
        self.__disponible = True

    def desactivar(self):
        self.__disponible = False

    def verificar_disponibilidad(self):
        if not self.__disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' no está disponible actualmente."
            )

    # ── Métodos abstractos (polimorfismo) ────────────────────────────────────

    @abstractmethod
    def calcular_costo(self, horas: float, **kwargs) -> float:
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        pass

    @abstractmethod
    def validar_parametros(self, horas: float, **kwargs) -> bool:
        pass

    # ── Método sobrecargado (con parámetros opcionales) ──────────────────────

    def calcular_costo_con_opciones(
        self,
        horas: float,
        con_iva: bool = True,
        descuento: float = 0.0,
        cargo_extra: float = 0.0
    ) -> dict:
        """
        Versión extendida del cálculo de costo.
        Simula sobrecarga de métodos con parámetros opcionales.

        Args:
            horas:       Duración en horas.
            con_iva:     Aplicar IVA del 19% (default: True).
            descuento:   Porcentaje de descuento 0-100 (default: 0).
            cargo_extra: Cargo adicional fijo en COP (default: 0).

        Returns:
            dict: Desglose completo del costo.

        Raises:
            DuracionInvalidaError: Si las horas son inválidas.
            CalculoCostoError:     Si los parámetros de cálculo son inválidos.
        """
        try:
            if horas <= 0:
                raise DuracionInvalidaError(f"Horas inválidas: {horas}")
            if not (0 <= descuento <= 100):
                raise CalculoCostoError(f"Descuento inválido: {descuento}%. Rango: 0-100.")
            if cargo_extra < 0:
                raise CalculoCostoError(f"Cargo extra negativo no permitido: {cargo_extra}")

            subtotal          = self.calcular_costo(horas)
            valor_descuento   = subtotal * (descuento / 100)
            base_con_dto      = subtotal - valor_descuento
            valor_iva         = base_con_dto * self.IVA if con_iva else 0.0
            total             = base_con_dto + valor_iva + cargo_extra

            return {
                "servicio":        self.nombre,
                "horas":           horas,
                "subtotal":        round(subtotal, 2),
                "descuento_pct":   descuento,
                "valor_descuento": round(valor_descuento, 2),
                "iva_pct":         self.IVA * 100 if con_iva else 0,
                "valor_iva":       round(valor_iva, 2),
                "cargo_extra":     round(cargo_extra, 2),
                "total":           round(total, 2),
            }

        except (DuracionInvalidaError, CalculoCostoError):
            raise
        except Exception as e:
            raise CalculoCostoError(f"Error inesperado en cálculo: {e}") from e

    # ── Métodos abstractos implementados ────────────────────────────────────

    def describir(self) -> str:
        estado = "Disponible ✓" if self.__disponible else "No disponible ✗"
        return (
            f"Servicio #{self.id}: {self.nombre} | "
            f"${self.__precio_base_hora:,.0f}/h | {estado}"
        )

    def validar(self) -> bool:
        return bool(self.nombre) and self.__precio_base_hora > 0

    def __str__(self) -> str:
        return f"Servicio[{self.id}]: {self.nombre} (${self.__precio_base_hora:,.0f}/h)"


# ────────────────────────────────────────────────────────────────────────────
# Servicio 1: ReservaSala
# ────────────────────────────────────────────────────────────────────────────

class ReservaSala(Servicio):
    """
    Alquiler de salas de reuniones o conferencias.
    Precio varía según equipamiento. Recargo nocturno del 20%.
    """

    CAP_MIN = 2
    CAP_MAX = 50
    PRECIO_BASE = 80_000  # COP/hora

    def __init__(
        self,
        nombre: str,
        capacidad_maxima: int,
        tiene_proyector: bool = True,
        tiene_videoconferencia: bool = False,
    ):
        if not isinstance(capacidad_maxima, int) or capacidad_maxima < self.CAP_MIN:
            raise CapacidadExcedidaError(
                f"Capacidad mínima: {self.CAP_MIN}. Recibido: {capacidad_maxima}"
            )
        if capacidad_maxima > self.CAP_MAX:
            raise CapacidadExcedidaError(
                f"Capacidad máxima: {self.CAP_MAX}. Recibido: {capacidad_maxima}"
            )

        precio = self.PRECIO_BASE
        if tiene_proyector:          precio += 10_000
        if tiene_videoconferencia:   precio += 30_000

        super().__init__(nombre, precio, f"Sala con cap. {capacidad_maxima} personas")
        self.__capacidad_maxima       = capacidad_maxima
        self.__tiene_proyector        = tiene_proyector
        self.__tiene_videoconferencia = tiene_videoconferencia

    @property
    def capacidad_maxima(self) -> int:
        return self.__capacidad_maxima

    def calcular_costo(self, horas: float, **kwargs) -> float:
        """
        Calcula el costo de la sala.
        kwargs admite: asistentes (int), nocturno (bool → recargo 20%).
        """
        self.validar_parametros(horas, **kwargs)
        costo = self.precio_base_hora * horas
        if kwargs.get("nocturno", False):
            costo *= 1.20
        return round(costo, 2)

    def describir_servicio(self) -> str:
        equip = []
        if self.__tiene_proyector:        equip.append("Proyector HD")
        if self.__tiene_videoconferencia: equip.append("Videoconferencia")
        eq_str = ", ".join(equip) if equip else "Básico"
        return (
            f"\n┌─ RESERVA DE SALA {'─' * 42}\n"
            f"│  Sala:         {self.nombre}\n"
            f"│  Capacidad:    {self.__capacidad_maxima} personas\n"
            f"│  Equipamiento: {eq_str}\n"
            f"│  Precio/hora:  ${self.precio_base_hora:,.0f} COP\n"
            f"│  Disponible:   {'Sí ✓' if self.disponible else 'No ✗'}\n"
            f"└{'─' * 58}"
        )

    def validar_parametros(self, horas: float, **kwargs) -> bool:
        if horas is None:
            raise DuracionInvalidaError("Debe especificar la duración en horas.")
        if horas < 1:
            raise DuracionInvalidaError(f"Duración mínima: 1 hora. Recibido: {horas}h")
        if horas > 12:
            raise DuracionInvalidaError(f"Duración máxima: 12 horas. Recibido: {horas}h")
        asistentes = kwargs.get("asistentes", 1)
        if asistentes > self.__capacidad_maxima:
            raise CapacidadExcedidaError(
                f"Sala '{self.nombre}': capacidad {self.__capacidad_maxima}, "
                f"solicitados {asistentes} asistentes."
            )
        return True


# ────────────────────────────────────────────────────────────────────────────
# Servicio 2: AlquilerEquipo
# ────────────────────────────────────────────────────────────────────────────

class AlquilerEquipo(Servicio):
    """
    Alquiler de equipos tecnológicos.
    Precio varía por tipo. Descuento del 10% para más de 3 unidades.
    """

    TIPOS_VALIDOS = {"laptop", "proyector", "camara", "microfono", "tablet", "servidor"}
    PRECIOS = {
        "laptop": 35_000, "proyector": 40_000, "camara": 50_000,
        "microfono": 15_000, "tablet": 25_000, "servidor": 80_000,
    }

    def __init__(self, nombre: str, tipo_equipo: str, cantidad_disponible: int):
        tipo = tipo_equipo.strip().lower() if tipo_equipo else ""
        if tipo not in self.TIPOS_VALIDOS:
            raise ServicioNoDisponibleError(
                f"Tipo '{tipo_equipo}' no válido. "
                f"Válidos: {', '.join(sorted(self.TIPOS_VALIDOS))}"
            )
        if not isinstance(cantidad_disponible, int) or cantidad_disponible <= 0:
            raise ParametroFaltanteError(
                f"Cantidad disponible debe ser un entero positivo. Recibido: {cantidad_disponible}"
            )

        super().__init__(nombre, self.PRECIOS[tipo], f"Alquiler de {tipo} – {nombre}")
        self.__tipo_equipo          = tipo
        self.__cantidad_disponible  = cantidad_disponible

    @property
    def tipo_equipo(self) -> str:
        return self.__tipo_equipo

    @property
    def cantidad_disponible(self) -> int:
        return self.__cantidad_disponible

    def calcular_costo(self, horas: float, **kwargs) -> float:
        """
        kwargs admite: cantidad (int → número de unidades, default 1).
        Descuento del 10% por volumen (> 3 unidades).
        """
        self.validar_parametros(horas, **kwargs)
        cantidad = kwargs.get("cantidad", 1)
        costo    = self.precio_base_hora * horas * cantidad
        if cantidad > 3:
            costo *= 0.90
        return round(costo, 2)

    def describir_servicio(self) -> str:
        return (
            f"\n┌─ ALQUILER DE EQUIPO {'─' * 40}\n"
            f"│  Equipo:       {self.nombre}\n"
            f"│  Tipo:         {self.__tipo_equipo.capitalize()}\n"
            f"│  Disponibles:  {self.__cantidad_disponible} unidad(es)\n"
            f"│  Precio/hora:  ${self.precio_base_hora:,.0f} COP por unidad\n"
            f"│  Descuento:    10% al alquilar más de 3 unidades\n"
            f"│  Disponible:   {'Sí ✓' if self.disponible else 'No ✗'}\n"
            f"└{'─' * 58}"
        )

    def validar_parametros(self, horas: float, **kwargs) -> bool:
        if horas is None or horas <= 0:
            raise DuracionInvalidaError(f"Duración inválida: {horas}")
        if horas > 72:
            raise DuracionInvalidaError(f"Máximo 72 horas. Recibido: {horas}h")
        cantidad = kwargs.get("cantidad", 1)
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ParametroFaltanteError(f"Cantidad inválida: {cantidad}")
        if cantidad > self.__cantidad_disponible:
            raise CapacidadExcedidaError(
                f"Solo hay {self.__cantidad_disponible} unidad(es) de '{self.nombre}'. "
                f"Solicitadas: {cantidad}"
            )
        return True


# ────────────────────────────────────────────────────────────────────────────
# Servicio 3: AsesoriaEspecializada
# ────────────────────────────────────────────────────────────────────────────

class AsesoriaEspecializada(Servicio):
    """
    Consultoría especializada con expertos en áreas tecnológicas.
    Precio según nivel del asesor. Descuento 15% en sesiones > 4h.
    Recargo del 30% si la asesoría es urgente.
    """

    NIVELES = {"junior": 1, "senior": 2, "experto": 3, "principal": 4}
    AREAS = {
        "desarrollo_software", "arquitectura", "ciberseguridad",
        "inteligencia_artificial", "gestion_proyectos", "infraestructura",
    }
    PRECIO_BASE = 120_000  # COP/hora nivel junior

    def __init__(
        self,
        nombre: str,
        area: str,
        nivel: str,
        nombre_asesor: str,
    ):
        area_l  = area.strip().lower()  if area  else ""
        nivel_l = nivel.strip().lower() if nivel else ""

        if area_l not in self.AREAS:
            raise ServicioNoDisponibleError(
                f"Área '{area}' no válida. Áreas: {', '.join(sorted(self.AREAS))}"
            )
        if nivel_l not in self.NIVELES:
            raise ServicioNoDisponibleError(
                f"Nivel '{nivel}' no válido. Niveles: {', '.join(self.NIVELES)}"
            )
        if not nombre_asesor or not nombre_asesor.strip():
            raise ParametroFaltanteError("El nombre del asesor es obligatorio.")

        precio = self.PRECIO_BASE * self.NIVELES[nivel_l]
        super().__init__(nombre, precio, f"Asesoría {area_l} – nivel {nivel_l}")
        self.__area          = area_l
        self.__nivel         = nivel_l
        self.__nombre_asesor = nombre_asesor.strip()

    @property
    def area(self) -> str:
        return self.__area

    @property
    def nivel(self) -> str:
        return self.__nivel

    @property
    def nombre_asesor(self) -> str:
        return self.__nombre_asesor

    def calcular_costo(self, horas: float, **kwargs) -> float:
        """
        kwargs admite: urgente (bool → recargo 30%).
        Descuento 15% si horas > 4.
        """
        self.validar_parametros(horas, **kwargs)
        costo = self.precio_base_hora * horas
        if horas > 4:
            costo *= 0.85
        if kwargs.get("urgente", False):
            costo *= 1.30
        return round(costo, 2)

    def describir_servicio(self) -> str:
        return (
            f"\n┌─ ASESORÍA ESPECIALIZADA {'─' * 36}\n"
            f"│  Servicio:     {self.nombre}\n"
            f"│  Área:         {self.__area.replace('_', ' ').title()}\n"
            f"│  Asesor:       {self.__nombre_asesor}\n"
            f"│  Nivel:        {self.__nivel.capitalize()}\n"
            f"│  Precio/hora:  ${self.precio_base_hora:,.0f} COP\n"
            f"│  Descuento:    15% si sesión > 4h | Recargo 30% si urgente\n"
            f"│  Disponible:   {'Sí ✓' if self.disponible else 'No ✗'}\n"
            f"└{'─' * 58}"
        )

    def validar_parametros(self, horas: float, **kwargs) -> bool:
        if horas is None:
            raise DuracionInvalidaError("Especifique la duración de la asesoría.")
        if horas < 0.5:
            raise DuracionInvalidaError(f"Mínimo 0.5h (30 min). Recibido: {horas}h")
        if horas > 8:
            raise DuracionInvalidaError(f"Máximo 8h por sesión. Recibido: {horas}h")
        return True


# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 6: CLASE Reserva
# ════════════════════════════════════════════════════════════════════════════

class Reserva(Entidad):
    """
    Integra un cliente con un servicio, una duración y un estado.

    Estados posibles: PENDIENTE → CONFIRMADA → CANCELADA / FINALIZADA

    Principios OOP:
    - Encapsulación: cliente, servicio y estado son privados.
    - Herencia: extiende Entidad.
    - Manejo de excepciones: confirmar, cancelar y procesar usan
      try/except, try/except/else, try/except/finally.
    """

    ESTADOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA", "FINALIZADA")

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        horas: float,
        parametros_extra: dict = None,
    ):
        """
        Args:
            cliente:          Objeto Cliente registrado en el sistema.
            servicio:         Objeto Servicio concreto.
            horas:            Duración en horas.
            parametros_extra: Parámetros adicionales para el servicio
                              (ej: asistentes, nocturno, urgente, cantidad).

        Raises:
            ReservaInvalidaError:      Si el cliente o servicio son None.
            ServicioNoDisponibleError:  Si el servicio no está disponible.
            DuracionInvalidaError:     Si la duración es inválida.
        """
        if cliente is None:
            raise ReservaInvalidaError("La reserva requiere un cliente válido.")
        if servicio is None:
            raise ReservaInvalidaError("La reserva requiere un servicio válido.")
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("El parámetro 'cliente' debe ser una instancia de Cliente.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("El parámetro 'servicio' debe ser una instancia de Servicio.")

        super().__init__(f"Reserva-{cliente.nombre[:8]}-{servicio.nombre[:8]}")

        # Verificar disponibilidad (lanza excepción si no está disponible)
        servicio.verificar_disponibilidad()

        # Validar parámetros del servicio específico
        params = parametros_extra or {}
        servicio.validar_parametros(horas, **params)

        self.__cliente          = cliente
        self.__servicio         = servicio
        self.__horas            = horas
        self.__parametros_extra = params
        self.__estado           = "PENDIENTE"
        self.__costo_calculado  = None
        self.__fecha_confirmacion = None

    # ── Propiedades ─────────────────────────────────────────────────────────

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def horas(self) -> float:
        return self.__horas

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def costo_calculado(self):
        return self.__costo_calculado

    # ── Operaciones de la reserva ────────────────────────────────────────────

    def confirmar(self) -> float:
        """
        Confirma la reserva, calcula el costo y lo asocia al cliente.
        Usa try/except/else/finally.

        Returns:
            Costo total calculado.

        Raises:
            OperacionNoPermitidaError: Si la reserva no está en estado PENDIENTE.
            CalculoCostoError:         Si falla el cálculo del costo.
        """
        if self.__estado != "PENDIENTE":
            raise OperacionNoPermitidaError(
                f"Solo se puede confirmar una reserva PENDIENTE. "
                f"Estado actual: {self.__estado}"
            )

        log = LoggerSistema()

        try:
            costo = self.__servicio.calcular_costo(
                self.__horas, **self.__parametros_extra
            )

        except (DuracionInvalidaError, CapacidadExcedidaError, CalculoCostoError) as e:
            # Encadenamiento de excepción: envolvemos el error original
            raise ReservaInvalidaError(
                f"No se pudo calcular el costo de la reserva #{self.id}: {e}"
            ) from e

        else:
            # Se ejecuta solo si NO hubo excepción en el bloque try
            self.__costo_calculado    = costo
            self.__estado             = "CONFIRMADA"
            self.__fecha_confirmacion = datetime.now()
            self.__cliente.agregar_reserva(self.id)
            log.exito(
                f"Reserva #{self.id} CONFIRMADA | Cliente: {self.__cliente.nombre} | "
                f"Servicio: {self.__servicio.nombre} | {self.__horas}h | "
                f"Costo: ${costo:,.0f} COP"
            )
            return costo

        finally:
            # Siempre se ejecuta, haya o no excepción
            log.info(f"Intento de confirmación de Reserva #{self.id} procesado.")

    def cancelar(self, motivo: str = "Sin motivo especificado"):
        """
        Cancela la reserva si está en estado PENDIENTE o CONFIRMADA.
        Usa try/except/finally.

        Raises:
            OperacionNoPermitidaError: Si la reserva ya fue cancelada o finalizada.
        """
        log = LoggerSistema()
        try:
            if self.__estado in ("CANCELADA", "FINALIZADA"):
                raise OperacionNoPermitidaError(
                    f"No se puede cancelar una reserva en estado '{self.__estado}'."
                )
            estado_anterior  = self.__estado
            self.__estado    = "CANCELADA"
            log.advertencia(
                f"Reserva #{self.id} CANCELADA | Estado anterior: {estado_anterior} | "
                f"Motivo: {motivo}"
            )
        except OperacionNoPermitidaError:
            raise
        except Exception as e:
            log.error(f"Error inesperado al cancelar Reserva #{self.id}: {e}")
            raise
        finally:
            log.info(f"Intento de cancelación de Reserva #{self.id} procesado.")

    def finalizar(self):
        """Marca la reserva como finalizada (servicio ejecutado)."""
        if self.__estado != "CONFIRMADA":
            raise OperacionNoPermitidaError(
                f"Solo se puede finalizar una reserva CONFIRMADA. Estado: {self.__estado}"
            )
        self.__estado = "FINALIZADA"
        LoggerSistema().info(f"Reserva #{self.id} marcada como FINALIZADA.")

    def obtener_desglose_costo(self, descuento: float = 0.0, con_iva: bool = True) -> dict:
        """
        Retorna el desglose completo del costo con opciones.
        Llama al método sobrecargado de Servicio.
        """
        return self.__servicio.calcular_costo_con_opciones(
            self.__horas,
            con_iva=con_iva,
            descuento=descuento,
            cargo_extra=0.0,
        )

    # ── Métodos abstractos implementados ────────────────────────────────────

    def describir(self) -> str:
        costo_str = f"${self.__costo_calculado:,.0f} COP" if self.__costo_calculado else "Sin calcular"
        conf_str  = self.__fecha_confirmacion.strftime("%Y-%m-%d %H:%M") if self.__fecha_confirmacion else "—"
        return (
            f"\n┌─ RESERVA #{self.id} {'─' * 46}\n"
            f"│  Cliente:      {self.__cliente.nombre}\n"
            f"│  Servicio:     {self.__servicio.nombre}\n"
            f"│  Duración:     {self.__horas}h\n"
            f"│  Estado:       {self.__estado}\n"
            f"│  Costo total:  {costo_str}\n"
            f"│  Confirmada:   {conf_str}\n"
            f"│  Creada:       {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}\n"
            f"└{'─' * 58}"
        )

    def validar(self) -> bool:
        return (
            self.__cliente is not None
            and self.__servicio is not None
            and self.__horas > 0
            and self.__estado in self.ESTADOS
        )

    def __str__(self) -> str:
        return (
            f"Reserva[{self.id}]: {self.__cliente.nombre} → "
            f"{self.__servicio.nombre} | {self.__horas}h | {self.__estado}"
        )


# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 7: GESTOR CENTRAL DEL SISTEMA
# ════════════════════════════════════════════════════════════════════════════

class GestorSistema:
    """
    Controlador central del sistema Software FJ.
    Administra listas de clientes, servicios y reservas en memoria.
    """

    def __init__(self):
        self.__clientes:  list[Cliente]  = []
        self.__servicios: list[Servicio] = []
        self.__reservas:  list[Reserva]  = []
        self.__log = LoggerSistema()

    # ── Gestión de Clientes ──────────────────────────────────────────────────

    def registrar_cliente(self, cliente: Cliente) -> bool:
        """
        Registra un cliente en el sistema.

        Returns:
            True si el registro fue exitoso.

        Raises:
            ClienteInvalidoError: Si el cliente no pasa la validación.
        """
        if not cliente.validar():
            raise ClienteInvalidoError(
                f"El cliente '{cliente.nombre}' no pasó la validación del sistema."
            )
        self.__clientes.append(cliente)
        self.__log.exito(f"Cliente registrado: {cliente}")
        return True

    def buscar_cliente(self, id_cliente: int) -> Cliente:
        """
        Busca un cliente por ID.

        Raises:
            ClienteInvalidoError: Si no se encuentra el cliente.
        """
        for c in self.__clientes:
            if c.id == id_cliente:
                return c
        raise ClienteInvalidoError(f"Cliente con ID {id_cliente} no encontrado.")

    # ── Gestión de Servicios ─────────────────────────────────────────────────

    def registrar_servicio(self, servicio: Servicio) -> bool:
        """Registra un servicio en el catálogo del sistema."""
        if not servicio.validar():
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no pasó la validación."
            )
        self.__servicios.append(servicio)
        self.__log.exito(f"Servicio registrado: {servicio}")
        return True

    # ── Gestión de Reservas ──────────────────────────────────────────────────

    def crear_reserva(
        self,
        cliente: Cliente,
        servicio: Servicio,
        horas: float,
        parametros_extra: dict = None,
    ) -> Reserva:
        """
        Crea y confirma una reserva automáticamente.

        Returns:
            Objeto Reserva confirmada.

        Raises:
            ReservaInvalidaError: Si no se puede crear o confirmar la reserva.
        """
        reserva = Reserva(cliente, servicio, horas, parametros_extra)
        reserva.confirmar()
        self.__reservas.append(reserva)
        return reserva

    # ── Reportes ─────────────────────────────────────────────────────────────

    def listar_clientes(self):
        if not self.__clientes:
            print("  (No hay clientes registrados)")
            return
        for c in self.__clientes:
            print(c.describir())

    def listar_servicios(self):
        if not self.__servicios:
            print("  (No hay servicios registrados)")
            return
        for s in self.__servicios:
            print(s.describir_servicio())

    def listar_reservas(self):
        if not self.__reservas:
            print("  (No hay reservas registradas)")
            return
        for r in self.__reservas:
            print(r.describir())

    def resumen_sistema(self):
        confirmadas = sum(1 for r in self.__reservas if r.estado == "CONFIRMADA")
        canceladas  = sum(1 for r in self.__reservas if r.estado == "CANCELADA")
        ingresos    = sum(r.costo_calculado for r in self.__reservas if r.costo_calculado)
        print(
            f"\n{'═' * 60}\n"
            f"  RESUMEN DEL SISTEMA - SOFTWARE FJ\n"
            f"{'═' * 60}\n"
            f"  Clientes registrados:  {len(self.__clientes)}\n"
            f"  Servicios disponibles: {len(self.__servicios)}\n"
            f"  Reservas totales:      {len(self.__reservas)}\n"
            f"    ✓ Confirmadas:       {confirmadas}\n"
            f"    ✗ Canceladas:        {canceladas}\n"
            f"  Ingresos generados:    ${ingresos:,.0f} COP\n"
            f"{'═' * 60}"
        )


# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 8: SIMULACIÓN DE OPERACIONES (10+ operaciones)
# ════════════════════════════════════════════════════════════════════════════

def ejecutar_simulacion():
    """
    Simula más de 10 operaciones completas incluyendo casos válidos e inválidos,
    demostrando el manejo robusto de excepciones y la estabilidad del sistema.
    """
    log    = LoggerSistema()
    gestor = GestorSistema()

    # ════════════════════════════════════════════════════════
    # OP 1-3: Registro de clientes (válidos)
    # ════════════════════════════════════════════════════════
    log.seccion("OPERACIONES 1-3: Registro de clientes válidos")

    try:
        c1 = Cliente("Ana María Torres", "ana.torres@empresa.com", "3001234567", "TechCorp")
        gestor.registrar_cliente(c1)
    except SistemaFJError as e:
        log.error(f"OP1 fallida: {e}")

    try:
        c2 = Cliente("Carlos Medina", "carlos.medina@gmail.com", "3157654321", "Freelance")
        gestor.registrar_cliente(c2)
    except SistemaFJError as e:
        log.error(f"OP2 fallida: {e}")

    try:
        c3 = Cliente("Laura Gómez", "lgomez@unad.edu.co", "6017890123", "UNAD")
        gestor.registrar_cliente(c3)
    except SistemaFJError as e:
        log.error(f"OP3 fallida: {e}")

    # ════════════════════════════════════════════════════════
    # OP 4-5: Registro de clientes INVÁLIDOS
    # ════════════════════════════════════════════════════════
    log.seccion("OPERACIONES 4-5: Registro de clientes inválidos")

    # OP 4: Email con formato inválido
    try:
        c_invalido = Cliente("Pedro Sin Email", "correo-invalido", "3001111111")
        gestor.registrar_cliente(c_invalido)
    except ParametroFaltanteError as e:
        log.error(f"OP4 – Parámetro faltante: {e}")
    except ClienteInvalidoError as e:
        log.error(f"OP4 – Cliente inválido (esperado): {e}")
    except SistemaFJError as e:
        log.error(f"OP4 – Error del sistema: {e}")
    finally:
        log.info("OP4 finalizada (con o sin error).")

    # OP 5: Nombre vacío
    try:
        c_vacio = Cliente("", "valido@mail.com", "3002222222")
        gestor.registrar_cliente(c_vacio)
    except ParametroFaltanteError as e:
        log.error(f"OP5 – Parámetro faltante (esperado): {e}")
    except ClienteInvalidoError as e:
        log.error(f"OP5 – Cliente inválido: {e}")
    finally:
        log.info("OP5 finalizada.")

    # ════════════════════════════════════════════════════════
    # OP 6: Registro de servicios válidos
    # ════════════════════════════════════════════════════════
    log.seccion("OPERACIÓN 6: Creación de servicios válidos")

    sala_a = asesor = equipo = None

    try:
        sala_a = ReservaSala("Sala Orion A", capacidad_maxima=20,
                             tiene_proyector=True, tiene_videoconferencia=True)
        gestor.registrar_servicio(sala_a)
        print(sala_a.describir_servicio())
    except SistemaFJError as e:
        log.error(f"OP6a – Sala: {e}")

    try:
        equipo = AlquilerEquipo("Laptop Dell XPS", tipo_equipo="laptop",
                                cantidad_disponible=10)
        gestor.registrar_servicio(equipo)
        print(equipo.describir_servicio())
    except SistemaFJError as e:
        log.error(f"OP6b – Equipo: {e}")

    try:
        asesor = AsesoriaEspecializada(
            "Consultoría IA Avanzada",
            area="inteligencia_artificial",
            nivel="experto",
            nombre_asesor="Dr. Ramón Vásquez",
        )
        gestor.registrar_servicio(asesor)
        print(asesor.describir_servicio())
    except SistemaFJError as e:
        log.error(f"OP6c – Asesoría: {e}")

    # ════════════════════════════════════════════════════════
    # OP 7: Servicio INVÁLIDO (tipo de equipo no reconocido)
    # ════════════════════════════════════════════════════════
    log.seccion("OPERACIÓN 7: Creación de servicio inválido")

    try:
        equipo_malo = AlquilerEquipo("Dron FPV", tipo_equipo="dron",
                                     cantidad_disponible=3)
        gestor.registrar_servicio(equipo_malo)
    except ServicioNoDisponibleError as e:
        log.error(f"OP7 – Servicio inválido (esperado): {e}")
    finally:
        log.info("OP7 finalizada.")

    # ════════════════════════════════════════════════════════
    # OP 8: Reserva EXITOSA con desglose de costo
    # ════════════════════════════════════════════════════════
    log.seccion("OPERACIÓN 8: Reserva exitosa con desglose de costo")

    reserva1 = None
    if c1 and sala_a:
        try:
            reserva1 = gestor.crear_reserva(
                c1, sala_a, horas=3,
                parametros_extra={"asistentes": 15, "nocturno": False}
            )
            print(reserva1.describir())

            # Desglose con IVA y 10% de descuento (método sobrecargado)
            desglose = reserva1.obtener_desglose_costo(descuento=10.0, con_iva=True)
            print(
                f"\n  Desglose con descuento 10% + IVA:\n"
                f"  Subtotal:       ${desglose['subtotal']:,.0f}\n"
                f"  Descuento:     -${desglose['valor_descuento']:,.0f}\n"
                f"  IVA (19%):     +${desglose['valor_iva']:,.0f}\n"
                f"  TOTAL:          ${desglose['total']:,.0f} COP"
            )
        except SistemaFJError as e:
            log.error(f"OP8 fallida: {e}")

    # ════════════════════════════════════════════════════════
    # OP 9: Reserva de equipo con múltiples unidades
    # ════════════════════════════════════════════════════════
    log.seccion("OPERACIÓN 9: Reserva de equipos con descuento por volumen")

    if c2 and equipo:
        try:
            reserva2 = gestor.crear_reserva(
                c2, equipo, horas=8,
                parametros_extra={"cantidad": 5}  # > 3 → descuento 10%
            )
            print(reserva2.describir())
        except SistemaFJError as e:
            log.error(f"OP9 fallida: {e}")

    # ════════════════════════════════════════════════════════
    # OP 10: Reserva FALLIDA – capacidad excedida
    # ════════════════════════════════════════════════════════
    log.seccion("OPERACIÓN 10: Reserva fallida por capacidad excedida")

    if c3 and sala_a:
        try:
            reserva_mala = gestor.crear_reserva(
                c3, sala_a, horas=2,
                parametros_extra={"asistentes": 99}  # Excede capacidad máxima (20)
            )
        except CapacidadExcedidaError as e:
            log.error(f"OP10 – Capacidad excedida (esperado): {e}")
        except ReservaInvalidaError as e:
            log.error(f"OP10 – Reserva inválida: {e}")
        finally:
            log.info("OP10 finalizada.")

    # ════════════════════════════════════════════════════════
    # OP 11: Reserva FALLIDA – duración inválida
    # ════════════════════════════════════════════════════════
    log.seccion("OPERACIÓN 11: Reserva fallida por duración inválida")

    if c1 and asesor:
        try:
            reserva_dur_mala = gestor.crear_reserva(c1, asesor, horas=15)
            # 15h excede el máximo de 8h para asesorías
        except DuracionInvalidaError as e:
            log.error(f"OP11 – Duración inválida (esperado): {e}")
        except ReservaInvalidaError as e:
            log.error(f"OP11 – Reserva inválida: {e}")
        finally:
            log.info("OP11 finalizada.")

    # ════════════════════════════════════════════════════════
    # OP 12: Cancelación de reserva + intento de recancelar
    # ════════════════════════════════════════════════════════
    log.seccion("OPERACIÓN 12: Cancelación y doble cancelación")

    if reserva1:
        try:
            reserva1.cancelar("Cliente solicitó reprogramación")
        except SistemaFJError as e:
            log.error(f"OP12a fallida: {e}")

        # Intentar cancelar una reserva ya cancelada (debe fallar)
        try:
            reserva1.cancelar("Intento duplicado")
        except OperacionNoPermitidaError as e:
            log.error(f"OP12b – Doble cancelación (esperado): {e}")
        finally:
            log.info("OP12 finalizada.")

    # ════════════════════════════════════════════════════════
    # OP 13: Asesoría urgente con desglose completo
    # ════════════════════════════════════════════════════════
    log.seccion("OPERACIÓN 13: Asesoría urgente con desglose completo")

    if c3 and asesor:
        try:
            reserva3 = gestor.crear_reserva(
                c3, asesor, horas=5,
                parametros_extra={"urgente": True}
            )
            print(reserva3.describir())
            desglose3 = reserva3.obtener_desglose_costo(descuento=5.0, con_iva=True)
            print(
                f"\n  Desglose asesoría urgente (descuento 5% + IVA):\n"
                f"  Subtotal:       ${desglose3['subtotal']:,.0f}\n"
                f"  Descuento:     -${desglose3['valor_descuento']:,.0f}\n"
                f"  IVA (19%):     +${desglose3['valor_iva']:,.0f}\n"
                f"  TOTAL:          ${desglose3['total']:,.0f} COP"
            )
        except SistemaFJError as e:
            log.error(f"OP13 fallida: {e}")

    # ════════════════════════════════════════════════════════
    # OP 14: Servicio desactivado no puede reservarse
    # ════════════════════════════════════════════════════════
    log.seccion("OPERACIÓN 14: Reserva sobre servicio desactivado")

    if equipo and c1:
        equipo.desactivar()
        log.advertencia(f"Servicio '{equipo.nombre}' desactivado manualmente.")
        try:
            reserva_inactiva = gestor.crear_reserva(c1, equipo, horas=4,
                                                    parametros_extra={"cantidad": 2})
        except ServicioNoDisponibleError as e:
            log.error(f"OP14 – Servicio no disponible (esperado): {e}")
        finally:
            equipo.activar()  # Reactivar para uso futuro
            log.info("OP14 finalizada. Servicio reactivado.")

    # ════════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ════════════════════════════════════════════════════════
    log.seccion("RESUMEN FINAL DEL SISTEMA")
    gestor.resumen_sistema()
    gestor.listar_reservas()

    print(
        f"\n{'═' * 60}\n"
        f"  Revisá el archivo '{LoggerSistema.ARCHIVO_LOG}'\n"
        f"  para ver el registro completo de eventos y errores.\n"
        f"{'═' * 60}\n"
    )


# ════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(
        f"\n{'═' * 70}\n"
        f"  SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ\n"
        f"  Curso Programación 213023 | UNAD\n"
        f"{'═' * 70}\n"
    )
    ejecutar_simulacion()

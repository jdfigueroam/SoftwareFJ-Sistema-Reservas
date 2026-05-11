"""
entidad.py
==========
Módulo que define la clase abstracta base Entidad para el sistema Software FJ.
Toda entidad del sistema (clientes, servicios, reservas) hereda de esta clase.

Autor: Equipo de desarrollo
Curso: Programación 213023 - UNAD
"""

from abc import ABC, abstractmethod
from datetime import datetime


class Entidad(ABC):
    """
    Clase abstracta base que representa cualquier entidad del sistema.

    Define la interfaz común que deben implementar todas las entidades,
    incluyendo identificación, descripción y validación.

    Principios OOP aplicados:
    - Abstracción: define el contrato general sin implementación concreta.
    - Encapsulación: el identificador se gestiona internamente.
    """

    _contador_global: int = 0

    def __init__(self, nombre: str):
        """
        Inicializa una entidad con un identificador único autoincremental.

        Args:
            nombre: Nombre descriptivo de la entidad.

        Raises:
            ValueError: Si el nombre está vacío o es None.
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de la entidad no puede estar vacío.")

        Entidad._contador_global += 1
        self.__id = Entidad._contador_global
        self.__nombre = nombre.strip()
        self.__fecha_creacion = datetime.now()

    # ── Propiedades (Encapsulación con getters) ─────────────────────────────

    @property
    def id(self) -> int:
        """Identificador único de la entidad (solo lectura)."""
        return self.__id

    @property
    def nombre(self) -> str:
        """Nombre de la entidad."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        """Permite modificar el nombre con validación."""
        if not valor or not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self.__nombre = valor.strip()

    @property
    def fecha_creacion(self) -> datetime:
        """Fecha y hora de creación de la entidad (solo lectura)."""
        return self.__fecha_creacion

    # ── Métodos abstractos (deben implementarse en subclases) ───────────────

    @abstractmethod
    def describir(self) -> str:
        """
        Retorna una descripción detallada de la entidad.
        Implementado por cada subclase (polimorfismo).
        """
        pass

    @abstractmethod
    def validar(self) -> bool:
        """
        Valida que la entidad tenga datos consistentes e íntegros.
        Retorna True si es válida, False en caso contrario.
        """
        pass

    # ── Métodos concretos comunes ───────────────────────────────────────────

    def obtener_info_base(self) -> dict:
        """
        Retorna un diccionario con la información base de la entidad.
        Útil para serialización o reportes.
        """
        return {
            "id": self.__id,
            "nombre": self.__nombre,
            "fecha_creacion": self.__fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": self.__class__.__name__
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.__id}, nombre='{self.__nombre}')"

    def __eq__(self, otro) -> bool:
        """Dos entidades son iguales si tienen el mismo ID."""
        if not isinstance(otro, Entidad):
            return NotImplemented
        return self.__id == otro.__id

    def __hash__(self) -> int:
        return hash(self.__id)

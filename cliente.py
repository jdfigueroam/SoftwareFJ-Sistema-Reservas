"""
cliente.py
==========
Módulo que define la clase Cliente con encapsulación robusta
y validaciones estrictas de datos personales.

Autor: Equipo de desarrollo
Curso: Programación 213023 - UNAD
"""

import re
from entidad import Entidad
from excepciones import ClienteInvalidoError, ParametroFaltanteError


class Cliente(Entidad):
    """
    Clase que representa a un cliente de Software FJ.

    Implementa encapsulación completa de datos personales,
    con validaciones estrictas en cada setter para garantizar
    la integridad de los datos.

    Hereda de: Entidad (clase abstracta base)

    Principios OOP aplicados:
    - Herencia: extiende Entidad.
    - Encapsulación: todos los atributos son privados con propiedades.
    - Polimorfismo: implementa describir() y validar() de forma propia.
    """

    # Expresión regular para validar emails
    _REGEX_EMAIL = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
    # Expresión regular para validar teléfonos (solo dígitos, 7-15 caracteres)
    _REGEX_TELEFONO = re.compile(r'^\+?[0-9]{7,15}$')

    def __init__(self, nombre: str, email: str, telefono: str, empresa: str = ""):
        """
        Inicializa un cliente con sus datos personales validados.

        Args:
            nombre:    Nombre completo del cliente.
            email:     Correo electrónico válido.
            telefono:  Número telefonico (7-15 dígitos).
            empresa:   Empresa u organización del cliente (opcional).

        Raises:
            ParametroFaltanteError: Si nombre, email o teléfono están vacíos.
            ClienteInvalidoError:   Si algún dato no cumple el formato requerido.
        """
        # Validar parámetros obligatorios antes de llamar al padre
        self._validar_parametros_requeridos(nombre, email, telefono)

        # Llamada al constructor de la clase padre
        try:
            super().__init__(nombre)
        except ValueError as e:
            raise ClienteInvalidoError(f"Nombre inválido: {e}") from e

        # Asignamos usando los setters para aplicar validaciones
        self.email = email
        self.telefono = telefono
        self.__empresa = empresa.strip() if empresa else "Particular"
        self.__activo = True
        self.__historial_reservas: list = []

    # ── Validaciones internas ───────────────────────────────────────────────

    @staticmethod
    def _validar_parametros_requeridos(nombre: str, email: str, telefono: str):
        """Verifica que los campos obligatorios no estén vacíos."""
        campos = {"nombre": nombre, "email": email, "telefono": telefono}
        for campo, valor in campos.items():
            if not valor or not str(valor).strip():
                raise ParametroFaltanteError(
                    f"El campo '{campo}' es obligatorio y no puede estar vacío."
                )

    # ── Propiedades (Encapsulación) ─────────────────────────────────────────

    @property
    def email(self) -> str:
        """Correo electrónico del cliente."""
        return self.__email

    @email.setter
    def email(self, valor: str):
        """Valida y asigna el email del cliente."""
        if not valor or not valor.strip():
            raise ParametroFaltanteError("El email es obligatorio.")
        valor = valor.strip().lower()
        if not self._REGEX_EMAIL.match(valor):
            raise ClienteInvalidoError(
                f"El email '{valor}' Validar un formato. "
                "Use el formato: usuario@dominio.com"
            )
        self.__email = valor

    @property
    def telefono(self) -> str:
        """Número de teléfono del cliente."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        """Valida y asigna el teléfono del cliente."""
        if not valor or not str(valor).strip():
            raise ParametroFaltanteError("El teléfono es obligatorio.")
        valor = str(valor).strip().replace(" ", "").replace("-", "")
        if not self._REGEX_TELEFONO.match(valor):
            raise ClienteInvalidoError(
                f"El teléfono '{valor}' no es válido. "
                "Debe contener entre 7 y 15 dígitos."
            )
        self.__telefono = valor

    @property
    def empresa(self) -> str:
        """Empresa u organización del cliente."""
        return self.__empresa

    @empresa.setter
    def empresa(self, valor: str):
        self.__empresa = valor.strip() if valor else "Particular"

    @property
    def activo(self) -> bool:
        """Indica si el cliente está activo en el sistema."""
        return self.__activo

    @property
    def historial_reservas(self) -> list:
        """Lista de IDs de reservas asociadas al cliente (solo lectura)."""
        return list(self.__historial_reservas)  # Retorna copia para proteger la lista

    # ── Métodos públicos ────────────────────────────────────────────────────

    def agregar_reserva(self, id_reserva: int):
        """
        Asocia una reserva al historial del cliente.

        Args:
            id_reserva: Identificador de la reserva a registrar.

        Raises:
            ClienteInvalidoError: Si el cliente no está activo.
        """
        if not self.__activo:
            raise ClienteInvalidoError(
                f"No se puede asignar una reserva al cliente '{self.nombre}' "
                "porque está inactivo."
            )
        if id_reserva not in self.__historial_reservas:
            self.__historial_reservas.append(id_reserva)

    def desactivar(self):
        """Desactiva el cliente, impidiendo nuevas reservas."""
        self.__activo = False

    def activar(self):
        """Reactiva un cliente previamente desactivado."""
        self.__activo = True

    def total_reservas(self) -> int:
        """Retorna el número total de reservas del cliente."""
        return len(self.__historial_reservas)

    # ── Implementación de métodos abstractos ───────────────────────────────

    def describir(self) -> str:
        """Retorna una descripción detallada del cliente."""
        estado = "Activo ✓" if self.__activo else "Inactivo ✗"
        return (
            f"┌─ CLIENTE #{self.id} ─────────────────────────────────\n"
            f"│  Nombre:    {self.nombre}\n"
            f"│  Email:     {self.__email}\n"
            f"│  Teléfono:  {self.__telefono}\n"
            f"│  Empresa:   {self.__empresa}\n"
            f"│  Estado:    {estado}\n"
            f"│  Reservas:  {self.total_reservas()}\n"
            f"│  Registrado: {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}\n"
            f"└────────────────────────────────────────────────────"
        )

    def validar(self) -> bool:
        """
        Valida la consistencia completa de los datos del cliente.

        Returns:
            True si todos los datos son válidos y consistentes.
        """
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

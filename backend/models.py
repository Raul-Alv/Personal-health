from typing import List
from pydantic import BaseModel
from enum import Enum

class Genero(str, Enum):
    masculino = "M"
    femenino = "F"

class EstadoCivil(str, Enum):
    soltero = "S"
    casado = "C"
    divorciado = "D"

# Create your models here.
class Paciente(BaseModel):
    id: str
    activo: bool
    nombre: str
    apellido: str
    genero: Genero
    telefono: str
    fecha_nacimiento: str
    direccion: str
    estado_civil: EstadoCivil

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class Practicante(BaseModel):
    id: str
    activo: bool
    nombre: str
    apellido: str
    genero: Genero
    telefono: str
    cualificacion: str

    def __str__(self):
        titulo = "Dr." if self.genero == Genero.masculino else "Dra."
        return f"{titulo} {self.nombre} {self.apellido}"

class Diente(BaseModel):
    codigo: str
    display: str
    diente: str

    def __str__(self):
        return f"{self.display}" 
    
class StatusProcedimiento(str, Enum):
    preparacion = 'preparation'
    en_progreso = 'in-progress'
    no_realizado = 'not-done'
    en_espera = 'on-hold'
    parado = 'stopped'
    completado = 'completed'
    con_errores = 'entered-in-error'
    desconocido = 'unknown'
    
class Procedimiento(BaseModel):
    id: str
    codigo: str
    status: StatusProcedimiento
    paciente: Paciente
    practicante: Practicante
    diente: Diente
    descripcion: str
    realizado_el: str

    def __str__(self):
        return f"{self.paciente.nombre} - {self.diente.display}, {self.realizado_el}"
    

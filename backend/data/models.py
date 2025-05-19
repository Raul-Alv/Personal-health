from typing import List
from pydantic import BaseModel, Enum

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
    activo = bool
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
        return f"{"Dr." if self.genero == "M" else "Dra."} {self.nombre} {self.apellido}"

class Diente(BaseModel):
    codigo: str
    display: str
    diente: str

    def __str__(self):
        return f"{self.display}" 
    
class StatusProcedimiento(str, Enum):
    preparacion = 'preparation', 'Preparación'
    en_progreso = 'in-progress', 'En Progreso'
    no_realizado = 'not-done', 'No Realizado'
    en_espera = 'on-hold', 'En Espera'
    parado = 'stopped', 'Parado'
    completado = 'completed', 'Completado'
    con_errores = 'entered-in-error', 'Con Errores'
    desconocido = 'unknown', 'Desconocido'
    
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
    

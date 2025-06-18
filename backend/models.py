from sqlalchemy import Column, String, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum

class Genero(enum.Enum):
    masculino = "M"
    femenino = "F"

class EstadoCivil(enum.Enum):
    soltero = "S"
    casado = "C"
    divorciado = "D"

# Create your models here.
class Paciente(Base):
    __tablename__ = "pacientes"
    id = Column(String, primary_key=True, index=True)
    activo = Column(Boolean, default=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    genero = Column(Enum(Genero), nullable=False)
    telefono = Column(String, nullable=True)
    fecha_nacimiento = Column(String, nullable=False)
    direccion = Column(String, nullable=True)
    estado_civil = Column(Enum(EstadoCivil), nullable=True)
    procedimientos = relationship("Procedimiento", back_populates="paciente")

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class Practicante(Base):
    __tablename__ = "practicantes"
    id = Column(String, primary_key=True, index=True)
    activo = Column(Boolean, default=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    genero = Column(Enum(Genero), nullable=False)
    telefono = Column(String, nullable=True)
    cualificacion = Column(String, nullable=True)
    procedimientos = relationship("Procedimiento", back_populates="practicante")

    def __str__(self):
        titulo = "Dr." if self.genero == Genero.masculino else "Dra."
        return f"{titulo} {self.nombre} {self.apellido}"

class Diente(Base):
    __tablename__ = "dientes"
    codigo = Column(String, primary_key=True, index=True)
    display = Column(String, nullable=False)
    procedimientos = relationship("Procedimiento", back_populates="diente")

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
    
class Procedimiento(Base):
    __tablename__ = "procedimientos"
    id = Column(String, primary_key=True, index=True)
    codigo = Column(String, nullable=False)
    status = Column(String, nullable=True)
    descripcion = Column(String, nullable=True)
    realizado_el = Column(String, nullable=True)

    paciente_id = Column(String, ForeignKey("pacientes.id"))
    practicante_id = Column(String, ForeignKey("practicantes.id"))
    diente_codigo = Column(String, ForeignKey("dientes.codigo"))

    paciente = relationship("Paciente", back_populates="procedimientos")
    practicante = relationship("Practicante", back_populates="procedimientos")
    diente = relationship("Diente", back_populates="procedimientos")

    def __str__(self):
        return f"{self.paciente.nombre} - {self.diente.display}, {self.realizado_el}"
    

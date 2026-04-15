# models/objeto.py

# Clase Padre
class Objeto:
    def __init__(self, nombre: str):
        self.nombre = nombre

# R2.1: Trampas Explosivas
class Trampa(Objeto):
    def __init__(self, nombre: str, alcance_explosion: int, dano_explosion: int):
        super().__init__(nombre)
        self.alcance_explosion = alcance_explosion
        self.dano_explosion = dano_explosion

# R2.2: Tesoros
class Tesoro(Objeto):
    def __init__(self, nombre: str, valor_monetario: int):
        super().__init__(nombre)
        self.valor_monetario = valor_monetario

# R2.3: Armamento y Defensa
class Equipamiento(Objeto):
    def __init__(self, nombre: str, aumento_ataque: int, aumento_defensa: int, precio_compra: int, precio_venta: int):
        super().__init__(nombre)
        self.aumento_ataque = aumento_ataque
        self.aumento_defensa = aumento_defensa
        self.precio_compra = precio_compra
        self.precio_venta = precio_venta
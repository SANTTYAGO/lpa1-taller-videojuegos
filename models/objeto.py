# models/objeto.py

class Objeto:
    def __init__(self, nombre: str, valor_monetario: int = 0):
        self.nombre = nombre
        self.valor_monetario = valor_monetario

class Tesoro(Objeto):
    def __init__(self, nombre: str, valor_monetario: int):
        super().__init__(nombre, valor_monetario)

class Trampa(Objeto):
    def __init__(self, nombre: str, dano_explosion: int, alcance_explosion: int = 1):
        super().__init__(nombre, 0)  # Las trampas no tienen valor monetario
        self.dano_explosion = dano_explosion
        self.alcance_explosion = alcance_explosion

class Equipamiento(Objeto):
    def __init__(self, nombre: str, aumento_ataque: int, aumento_defensa: int, precio_compra: int = 0, valor_venta: int = 0):
        super().__init__(nombre, valor_venta)
        self.aumento_ataque = aumento_ataque
        self.aumento_defensa = aumento_defensa
        self.precio_compra = precio_compra

# --- NUEVO: Herencia para objetos de un solo uso ---
class Consumible(Objeto):
    def __init__(self, nombre: str, tipo_restauracion: str, cantidad: int, precio_compra: int = 50):
        # Al venderlo, te dan la mitad de lo que costó
        super().__init__(nombre, precio_compra // 2)
        self.tipo_restauracion = tipo_restauracion # Puede ser "HP" (Vida) o "MP" (Maná)
        self.cantidad = cantidad
        self.precio_compra = precio_compra

    def usar(self, personaje):
        """Aplica el efecto al personaje y limita el máximo usando min()"""
        if self.tipo_restauracion == "HP":
            personaje.puntos_vida = min(personaje.puntos_vida_max, personaje.puntos_vida + self.cantidad)
            print(f"💚 {personaje.nombre} se curó {self.cantidad} de Vida.")
        elif self.tipo_restauracion == "MP":
            personaje.puntos_magia = min(personaje.puntos_magia_max, personaje.puntos_magia + self.cantidad)
            print(f"💧 {personaje.nombre} recuperó {self.cantidad} de Maná.")
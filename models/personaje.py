# models/personaje.py
from models.objeto import Equipamiento
import random

class Personaje:
    def __init__(self, nombre: str, puntos_vida: int, puntos_magia: int, ataque: int, defensa: int):
        self.nombre = nombre
        self.puntos_vida = puntos_vida
        self.puntos_vida_max = puntos_vida 
        self.puntos_magia = puntos_magia
        self.puntos_magia_max = puntos_magia
        
        self.ataque = ataque
        self.defensa = defensa
        self.nivel = 1
        self.experiencia = 0
        self.puntaje = 0
        self.zonas_exploradas = 0
        self.inventario = []
        
        self.arma_equipada = None 
        self.armadura_equipada = None
        self.estados = {"veneno": 0, "aturdido": 0}

    def aplicar_estado(self, estado: str, turnos: int):
        self.estados[estado] = turnos

    def procesar_estados(self):
        mensajes = []
        aturdido = False
        dano_total = 0

        if self.estados["veneno"] > 0:
            dano = 5 
            self.recibir_dano(dano)
            self.estados["veneno"] -= 1
            dano_total += dano
            mensajes.append(f"El Veneno consume {dano} HP.")

        if self.estados["aturdido"] > 0:
            aturdido = True
            self.estados["aturdido"] -= 1
            mensajes.append("¡Estás Aturdido y no puedes moverte!")

        return aturdido, mensajes, dano_total

    def esta_vivo(self) -> bool:
        return self.puntos_vida > 0

    def mostrar_estadisticas(self):
        pass 

    def recolectar_objeto(self, objeto):
        self.inventario.append(objeto)

    def equipar(self, equipamiento: Equipamiento):
        if equipamiento.tipo == "arma":
            if self.arma_equipada:
                self.ataque -= self.arma_equipada.aumento_ataque
                self.defensa -= self.arma_equipada.aumento_defensa
                self.inventario.append(self.arma_equipada) 
            self.arma_equipada = equipamiento
            
        elif equipamiento.tipo == "armadura":
            if self.armadura_equipada:
                self.ataque -= self.armadura_equipada.aumento_ataque
                self.defensa -= self.armadura_equipada.aumento_defensa
                self.inventario.append(self.armadura_equipada) 
            self.armadura_equipada = equipamiento
        
        self.ataque += equipamiento.aumento_ataque
        self.defensa += equipamiento.aumento_defensa
        
        if equipamiento in self.inventario:
            self.inventario.remove(equipamiento) 

    def recibir_dano(self, cantidad: int):
        # --- NUEVO: Probabilidad de esquivar del Pícaro ---
        # Verificamos si la instancia actual es de tipo Picaro
        if isinstance(self, Picaro):
            # 20% de probabilidad de esquivar el daño por completo
            if random.random() < 0.20:
                print(f"¡{self.nombre} ha esquivado el ataque!")
                return False # Retornamos False para indicar que no hubo daño

        self.puntos_vida -= cantidad
        if self.puntos_vida < 0:
            self.puntos_vida = 0
        return True

    def ganar_experiencia(self, cantidad: int):
        self.experiencia += cantidad
        if self.experiencia >= 100:
            self.subir_nivel()

    def subir_nivel(self):
        self.nivel += 1
        self.experiencia -= 100 
        self.puntos_vida_max += 20
        self.puntos_vida = self.puntos_vida_max 
        self.puntos_magia_max += 15
        self.puntos_magia = self.puntos_magia_max
        self.ataque += 5
        self.defensa += 3
        self.estados["veneno"] = 0
        self.estados["aturdido"] = 0

    def ganar_puntaje(self, cantidad: int):
        self.puntaje += cantidad

    def registrar_exploracion(self):
        self.zonas_exploradas += 1


# --- NUEVAS CLASES HIJAS ---

class Caballero(Personaje):
    def __init__(self, nombre: str):
        # Llama al constructor de Personaje con estadísticas únicas
        # Alta vida (150) y defensa (8), poca magia (20)
        super().__init__(nombre=f"Sir {nombre}", puntos_vida=150, puntos_magia=20, ataque=15, defensa=8)

class Mago(Personaje):
    def __init__(self, nombre: str):
        # Baja vida (70) y defensa (2), pero altísima magia (120) y ataque inicial (20)
        super().__init__(nombre=f"{nombre} el Sabio", puntos_vida=70, puntos_magia=120, ataque=20, defensa=2)

class Picaro(Personaje):
    def __init__(self, nombre: str):
        # Stats balanceadas (100 HP, 50 MP, 12 ATK, 4 DEF)
        # La magia de esta clase está en su pasiva de esquivar (en Personaje.recibir_dano) y crítico
        super().__init__(nombre=f"{nombre} Sombra", puntos_vida=100, puntos_magia=50, ataque=12, defensa=4)
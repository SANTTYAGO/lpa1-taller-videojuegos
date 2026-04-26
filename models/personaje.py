# models/personaje.py
from models.objeto import Equipamiento

class Personaje:
    def __init__(self, nombre: str, puntos_vida: int, ataque: int, defensa: int):
        self.nombre = nombre
        self.puntos_vida = puntos_vida
        self.puntos_vida_max = puntos_vida 
        self.puntos_magia = 50
        self.puntos_magia_max = 50
        
        self.ataque = ataque
        self.defensa = defensa
        self.nivel = 1
        self.experiencia = 0
        self.puntaje = 0
        self.zonas_exploradas = 0
        self.inventario = []
        
        # --- NUEVO: Ranuras de equipo separadas ---
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
        pass # Omitido en terminal para enfocarnos en la UI gráfica

    def recolectar_objeto(self, objeto):
        self.inventario.append(objeto)

    # --- NUEVO: Lógica de equipamiento inteligente ---
    def equipar(self, equipamiento: Equipamiento):
        if equipamiento.tipo == "arma":
            if self.arma_equipada:
                self.ataque -= self.arma_equipada.aumento_ataque
                self.defensa -= self.arma_equipada.aumento_defensa
                self.inventario.append(self.arma_equipada) # Devuelve la vieja a la mochila
            self.arma_equipada = equipamiento
            
        elif equipamiento.tipo == "armadura":
            if self.armadura_equipada:
                self.ataque -= self.armadura_equipada.aumento_ataque
                self.defensa -= self.armadura_equipada.aumento_defensa
                self.inventario.append(self.armadura_equipada) # Devuelve la vieja a la mochila
            self.armadura_equipada = equipamiento
        
        # Aplicamos los nuevos stats
        self.ataque += equipamiento.aumento_ataque
        self.defensa += equipamiento.aumento_defensa
        
        # Retiramos el objeto de la mochila
        if equipamiento in self.inventario:
            self.inventario.remove(equipamiento) 

    def recibir_dano(self, cantidad: int):
        self.puntos_vida -= cantidad
        if self.puntos_vida < 0:
            self.puntos_vida = 0

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
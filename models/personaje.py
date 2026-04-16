# models/personaje.py
from models.objeto import Equipamiento

class Personaje:
    def __init__(self, nombre: str, puntos_vida: int, ataque: int, defensa: int):
        self.nombre = nombre
        self.puntos_vida = puntos_vida
        self.puntos_vida_max = puntos_vida # Para saber el tope al curarse o subir de nivel
        self.ataque = ataque
        self.defensa = defensa
        self.nivel = 1
        self.experiencia = 0
        self.inventario = []
        self.equipamiento_actual = None # R3.3: Espacio para el arma/armadura equipada

    def esta_vivo(self) -> bool:
        return self.puntos_vida > 0

    def mostrar_estadisticas(self):
        print(f"--- {self.nombre} (Nivel {self.nivel} | EXP: {self.experiencia}/100) ---")
        print(f"HP: {self.puntos_vida}/{self.puntos_vida_max} | ATK: {self.ataque} | DEF: {self.defensa}")
        if self.equipamiento_actual:
            print(f"Equipado: {self.equipamiento_actual.nombre}")
        print(f"Inventario: {len(self.inventario)} objetos")

    # Requerimiento R3.2: Recolectar objetos
    def recolectar_objeto(self, objeto):
        self.inventario.append(objeto)
        print(f"🎒 {self.nombre} ha guardado '{objeto.nombre}' en su inventario.")

    # Requerimiento R3.3: Usar equipamiento
    def equipar(self, equipamiento: Equipamiento):
        if self.equipamiento_actual:
            # Si ya tiene algo equipado, le restamos los bonos anteriores
            self.ataque -= self.equipamiento_actual.aumento_ataque
            self.defensa -= self.equipamiento_actual.aumento_defensa
            self.inventario.append(self.equipamiento_actual)
            print(f"🔄 {self.nombre} se ha desequipado '{self.equipamiento_actual.nombre}'.")
        
        # Equipamos el nuevo objeto y sumamos los bonos
        self.equipamiento_actual = equipamiento
        self.ataque += equipamiento.aumento_ataque
        self.defensa += equipamiento.aumento_defensa
        if equipamiento in self.inventario:
            self.inventario.remove(equipamiento) # Lo sacamos del inventario al usarlo
        print(f"⚔️ {self.nombre} se ha equipado '{equipamiento.nombre}' (+{equipamiento.aumento_ataque} ATK, +{equipamiento.aumento_defensa} DEF).")

    # Requerimientos R6.1 y R6.2: Ganar experiencia y subir de nivel
    def ganar_experiencia(self, cantidad: int):
        self.experiencia += cantidad
        print(f"✨ {self.nombre} ha ganado {cantidad} puntos de experiencia.")
        
        # Verificamos si alcanza los 100 puntos para subir de nivel
        if self.experiencia >= 100:
            self.subir_nivel()

    def subir_nivel(self):
        self.nivel += 1
        self.experiencia -= 100 # Reiniciamos la barra de experiencia
        
        # Mejora de atributos por nivel (R6.2)
        self.puntos_vida_max += 20
        self.puntos_vida = self.puntos_vida_max # Le curamos la vida al subir de nivel
        self.ataque += 5
        self.defensa += 3
        
        print(f"\n🎉 ¡Felicidades! {self.nombre} ha alcanzado el Nivel {self.nivel}! 🎉")
        print("Tus atributos han aumentado.")
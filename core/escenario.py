# core/escenario.py
import random
from models.enemigo import Enemigo
from models.objeto import Tesoro, Trampa, Equipamiento

class Zona:
    def __init__(self, id_zona: int):
        self.id_zona = id_zona
        self.nombre = f"Área {id_zona}"
        self.enemigo = None
        self.objeto = None
        self.es_tienda = False

    def mostrar_info(self):
        print(f"\n🗺️ --- {self.nombre} ---")
        if self.es_tienda:
            print("🏪 ¡Es una Zona Segura! Hay un mercader aquí dispuesto a comerciar.")
        
        if self.enemigo:
            print(f"⚠️ Peligro inminente: Un '{self.enemigo.nombre}' acecha en las sombras.")
            
        if self.objeto:
            print(f"📦 Has avistado algo en el suelo: {self.objeto.nombre}.")
            
        if not self.es_tienda and not self.enemigo and not self.objeto:
            print("🍃 Un lugar tranquilo. No hay amenazas ni objetos a la vista.")

class Escenario:
    def __init__(self):
        # R4.1: Generación de escenario con 20 áreas explorables
        self.zonas = [Zona(i) for i in range(1, 21)]
        self.generar_entorno()

    def generar_entorno(self):
        # R4.3: Zonas de venta (Establecemos 2 tiendas aleatorias en el mapa)
        tiendas_ids = random.sample(range(20), 2)
        for i in tiendas_ids:
            self.zonas[i].es_tienda = True
            self.zonas[i].nombre = "Refugio del Mercader"

        # R4.2: Distribución de Elementos
        # Repartimos 17 elementos aleatorios en las zonas que no son tiendas
        zonas_disponibles = [z for z in self.zonas if not z.es_tienda]
        zonas_seleccionadas = random.sample(zonas_disponibles, 17)
        
        for zona in zonas_seleccionadas:
            # 50% de probabilidad de que aparezca un enemigo o un objeto
            if random.choice([True, False]):
                # Generar enemigo aleatorio
                tipos = ["volador", "terrestre"]
                zona.enemigo = Enemigo(
                    nombre=random.choice(["Esqueleto", "Limo", "Murciélago", "Goblin"]),
                    puntos_vida=random.randint(20, 50),
                    ataque=random.randint(5, 15),
                    defensa=random.randint(2, 8),
                    tipo=random.choice(tipos)
                )
            else:
                # Generar objeto aleatorio
                if random.choice([True, False]):
                    zona.objeto = Tesoro("Bolsa de Monedas", random.randint(10, 100))
                else:
                    zona.objeto = Trampa("Mina Oculta", alcance_explosion=1, dano_explosion=25)
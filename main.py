# main.py
from models.personaje import Personaje
from core.escenario import Escenario

def main():
    print("--- GENERANDO EL MUNDO DE JUEGO ---\n")
    
    # Instanciamos al jugador
    heroe = Personaje(nombre="Explorador", puntos_vida=100, ataque=15, defensa=10)
    
    # 1. Generamos el escenario completo (R4.1, R4.2, R4.3)
    mundo = Escenario()
    print("¡El mundo ha sido creado! El mapa consta de 20 zonas misteriosas.")
    
    # 2. Simulamos la exploración de los primeros 5 cuartos
    print("\n--- INICIANDO EXPLORACIÓN ---")
    for i in range(5): # Recorremos de la zona índice 0 al 4
        zona_actual = mundo.zonas[i]
        zona_actual.mostrar_info()
        
        # Pequeña interacción de ejemplo
        if zona_actual.objeto:
            heroe.recolectar_objeto(zona_actual.objeto)
            zona_actual.objeto = None # Lo quitamos del mapa
            
    print("\n--- ESTADO DEL INVENTARIO ---")
    heroe.mostrar_estadisticas()

if __name__ == "__main__":
    main()
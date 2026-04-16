# main.py
from models.personaje import Personaje
from models.objeto import Equipamiento

def main():
    print("--- PRUEBA DE PROGRESIÓN Y EQUIPAMIENTO ---\n")
    
    # 1. Instanciar al jugador
    heroe = Personaje(nombre="Caballero", puntos_vida=100, ataque=20, defensa=15)
    heroe.mostrar_estadisticas()
    print("\n------------------------------------------------")

    # 2. Encontrar y equipar un objeto (R3.3)
    espada_acero = Equipamiento(nombre="Espada de Acero", aumento_ataque=12, aumento_defensa=2, precio_compra=150, precio_venta=75)
    heroe.recolectar_objeto(espada_acero)
    heroe.equipar(espada_acero)
    
    print("\n--- ESTADÍSTICAS TRAS EQUIPAR ARMA ---")
    heroe.mostrar_estadisticas()
    print("------------------------------------------------\n")

    # 3. Simular ganancia de experiencia por derrotar a un enemigo (R6.1 y R6.2)
    print("⚔️ El héroe ha derrotado a un Orco de Élite...")
    heroe.ganar_experiencia(120) # Esto debería provocar que suba de nivel directamente
    
    print("\n--- ESTADÍSTICAS TRAS SUBIR DE NIVEL ---")
    heroe.mostrar_estadisticas()

if __name__ == "__main__":
    main()
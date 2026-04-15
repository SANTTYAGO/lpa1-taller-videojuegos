# main.py
from models.personaje import Personaje
from models.enemigo import Enemigo
from models.objeto import Trampa, Tesoro, Equipamiento

def main():
    print("--- INICIANDO MOTOR DEL JUEGO ---\n")
    
    # 1. Instanciar al jugador principal
    heroe = Personaje(nombre="Caballero", puntos_vida=100, ataque=20, defensa=15)
    heroe.mostrar_estadisticas()
    print("")

    # 2. Instanciar enemigos de prueba
    orco = Enemigo(nombre="Orco Furioso", puntos_vida=50, ataque=12, defensa=5, tipo="terrestre")
    gargola = Enemigo(nombre="Gárgola Oscura", puntos_vida=30, ataque=15, defensa=8, tipo="volador")
    
    orco.mostrar_estadisticas()
    gargola.mostrar_estadisticas()
    print("")

    # 3. Instanciar objetos de prueba en el entorno
    moneda_oro = Tesoro(nombre="Cáliz Antiguo", valor_monetario=250)
    mina_terrestre = Trampa(nombre="Mina de Pólvora", alcance_explosion=2, dano_explosion=40)
    espada_hierro = Equipamiento(nombre="Espada de Hierro", aumento_ataque=10, aumento_defensa=2, precio_compra=100, precio_venta=50)

    print("--- OBJETOS GENERADOS EN EL MAPA ---")
    print(f"Tesoro: {moneda_oro.nombre} (Valor: {moneda_oro.valor_monetario} oro)")
    print(f"Peligro: {mina_terrestre.nombre} (Daño: {mina_terrestre.dano_explosion} HP)")
    print(f"Mercader ofrece: {espada_hierro.nombre} por {espada_hierro.precio_compra} oro (+{espada_hierro.aumento_ataque} ATK)")

if __name__ == "__main__":
    main()
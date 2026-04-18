# main.py
from models.personaje import Personaje
from models.enemigo import Enemigo
from core.escenario import Escenario
from core.combate import SistemaCombate
from ui.pantalla import MotorGrafico

# # Constantes de Victoria
# PUNTAJE_VICTORIA = 500
# TOTAL_ZONAS = 20

# def evaluar_victoria(heroe: Personaje) -> bool:
#     # R7.1: Victoria por Exploración
#     if heroe.zonas_exploradas >= TOTAL_ZONAS:
#         print("\n👑 ¡VICTORIA! Has explorado todos los rincones del mapa. Eres un verdadero aventurero.")
#         return True
        
#     # R7.3: Victoria por Puntaje
#     if heroe.puntaje >= PUNTAJE_VICTORIA:
#         print(f"\n👑 ¡VICTORIA! Has alcanzado {heroe.puntaje} puntos, asegurando tu fama y fortuna.")
#         return True
        
#     return False

# def main():
#     print("--- INICIANDO AVENTURA (VERSIÓN TEXTO) ---\n")
    
#     heroe = Personaje(nombre="Caballero", puntos_vida=150, ataque=25, defensa=15)
#     mundo = Escenario()
    
#     juego_activo = True
#     zona_actual_idx = 0

#     # Bucle Principal de Juego
#     while juego_activo and zona_actual_idx < TOTAL_ZONAS:
#         zona = mundo.zonas[zona_actual_idx]
#         zona.mostrar_info()
#         heroe.registrar_exploracion()
        
#         # Interacción con la zona
#         if zona.enemigo:
#             SistemaCombate.iniciar_combate(heroe, zona.enemigo)
#             if heroe.esta_vivo():
#                 heroe.ganar_experiencia(50)
#                 heroe.ganar_puntaje(100) # Gana puntos al vencer enemigos
                
#                 # R7.2: Verificar si derrotamos al Jefe Final
#                 if zona.enemigo.nombre == "Rey Demonio":
#                     print("\n👑 ¡VICTORIA SUPREMA! El Rey Demonio ha caído. Has salvado el mundo.")
#                     break
#             else:
#                 juego_activo = False # Game Over
                
#         elif zona.objeto:
#             if hasattr(zona.objeto, 'dano_explosion'):
#                 print(f"💥 ¡Pisas una {zona.objeto.nombre}! Recibes {zona.objeto.dano_explosion} de daño.")
#                 heroe.recibir_dano(zona.objeto.dano_explosion)
#                 if not heroe.esta_vivo():
#                     print("💀 Has muerto por una trampa. Fin del juego.")
#                     juego_activo = False
#             else:
#                 heroe.recolectar_objeto(zona.objeto)
#                 heroe.ganar_puntaje(50) # Gana puntos al encontrar objetos
                
#         # Evaluación de victoria general (Puntaje o Exploración)
#         if evaluar_victoria(heroe):
#             break
            
#         # Avanzar a la siguiente zona simulando input del jugador
#         input("\nPresiona ENTER para avanzar a la siguiente zona...")
#         zona_actual_idx += 1

#     print("\n--- RESUMEN FINAL ---")
#     heroe.mostrar_estadisticas()

def main():
    print("Iniciando motor gráfico...")
    
    heroe_principal = Personaje(nombre="Santi", puntos_vida=100, ataque=20, defensa=15)

    orco = Enemigo(nombre="Orco Furioso", puntos_vida=50, ataque=12, defensa=5, tipo="terrestre")

    juego = MotorGrafico(heroe=heroe_principal, enemigo_prueba=orco)

    # Este es el "Game Loop" universal de todo videojuego
    while juego.corriendo:
        juego.manejar_eventos() # Leer teclado/mouse
        juego.dibujar()         # Renderizar gráficos
        juego.actualizar()      # Controlar FPS
        
    juego.salir()
    print("Juego cerrado correctamente.")

if __name__ == "__main__":
    main()
# core/combate.py

class SistemaCombate:
    
    @staticmethod
    def calcular_dano(ataque: int, defensa: int) -> int:
        # R5.2: Cálculo de daño mitigado por la defensa
        # Usamos una fórmula sencilla: el ataque menos la mitad de la defensa del rival
        dano = ataque - (defensa // 2)
        return dano if dano > 0 else 1 # Siempre se hace al menos 1 punto de daño

    @staticmethod
    def iniciar_combate(personaje, enemigo):
        print(f"\n⚔️ --- ¡COMIENZA EL COMBATE: {personaje.nombre} VS {enemigo.nombre}! --- ⚔️")
        
        # R5.1: Mecánica de Combate por turnos
        while personaje.esta_vivo() and enemigo.esta_vivo():
            # 1. Turno del Jugador
            dano_al_enemigo = SistemaCombate.calcular_dano(personaje.ataque, enemigo.defensa)
            enemigo.recibir_dano(dano_al_enemigo)
            print(f"🗡️ {personaje.nombre} ataca causando {dano_al_enemigo} de daño. HP {enemigo.nombre}: {enemigo.puntos_vida}")
            
            if not enemigo.esta_vivo():
                print(f"🏆 ¡{enemigo.nombre} ha sido derrotado!")
                break
                
            # 2. Turno del Enemigo
            dano_al_personaje = SistemaCombate.calcular_dano(enemigo.ataque, personaje.defensa)
            personaje.recibir_dano(dano_al_personaje)
            print(f"👹 {enemigo.nombre} contraataca causando {dano_al_personaje} de daño. HP {personaje.nombre}: {personaje.puntos_vida}")
            
            if not personaje.esta_vivo():
                print(f"💀 {personaje.nombre} ha caído en batalla. Fin del juego.")
                break
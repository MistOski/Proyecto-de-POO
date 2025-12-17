Ignacio Millapani
ignaciojavier.millapani@alumnos.ulagos.cl

Descripción del Proyecto: Videojuego de Estrategia en Pygame

Este proyecto consiste en un videojuego de estrategia desarrollado utilizando Pygame, cuyo objetivo principal es la gestión y expansión territorial dentro de la Región de los Lagos.

Los jugadores comienzan seleccionando una ciudad inicial, que al iniciar una nueva partida recibe asignación de una clase aleatoria. A partir de allí, deben administrar sus recursos, tomar decisiones estratégicas y progresar en la conquista de ciudades vecinas, con la meta final de dominar toda la región.

El juego se ejecuta mediante el comando: python main.py

Al iniciar, se despliega la pantalla de inicio, la cual se activa presionando la tecla INTRO.

Cada ciudad dentro del juego realiza una acción automática cada 30 segundos, que puede incluir comerciar, recolectar recursos o intentar conquistar otras ciudades (esta última función se encuentra actualmente deshabilitada). El sistema de conquista está diseñado para permitir la obtención de monedas y expansión territorial, pero las conquistas solo pueden efectuarse sobre ciudades próximas al territorio inicial del jugador; las ciudades alejadas requieren una expansión progresiva a través de las ciudades intermedias.

Aunque el juego aún no cuenta con una interfaz gráfica completa, se encuentran implementadas funcionalidades clave, entre ellas:

Pestaña de notificaciones: ubicada en la esquina inferior izquierda, informa sobre las acciones del jugador y de las demás ciudades.

Acciones disponibles: mediante las teclas 1, 2, 3 y 4, el jugador puede seleccionar entre atacar, comerciar, recolectar o extorsionar, desplegándose un menú contextual para elegir la ciudad objetivo en caso de ataques.

Este proyecto combina elementos de gestión de recursos, estrategia territorial y toma de decisiones tácticas, ofreciendo una base sólida para futuras expansiones y mejoras de interfaz gráfica.

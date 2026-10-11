# Tarefa Optativa 2

Abre: sexta-feira, 14 ago. 2026, 10:00

Vencimento: quinta-feira, 20 ago. 2026, 23:59

Escreva um programa, em qualquer linguagem, com as seguintes especificações:

## Dados de entrada

1) Número n de forças, n >= 1.

2) Componentes (F_xi, F_yi, F_zi) das n forças aplicadas a um corpo rígido.

3) Coordenadas (x_i, y_i, z_i) dos respectivos pontos de aplicação das n forças ao corpo rígido.

4) Coordenadas (x_Q, y_Q, z_Q) de um polo Q do corpo rígido.

5) Coordenadas (x_A, y_A, z_A) de um segundo polo A do corpo rígido.

6) Componentes (u_x, u_y, u_z) de um versor u.

## Dados de saída

a) Resultante R do sistema de forças.

b) Momento M_Q resultante do sistema de forças no polo Q.

c) Momento M_A resultante do sistema de forças no polo A.

d) Torque no eixo Au.

e) Invariante escalar I do sistema de forças.

f) Caracterização do sistema de forças: dizer se ele é redutível a um binário, redutível a uma única força, redutível a força + binário, ou se é nulo.

g) Caso o sistema não seja nulo ou redutível a um binário, determinar o seu eixo central e o momento mínimo.

h) Desenhar uma figura contendo o sistema de referência Oxyz, as forças F_i e seus pontos de aplicação P_i, o polo Q, o eixo Au, a resultante R (quando não nula), os momentos M_Q e M_A (quando não nulos).

i) Caso o sistema de forças tenha eixo central, desenhar uma segunda figura contendo o sistema de referência Oxyz, as forças F_i e seus pontos de aplicação P_i, o polo Q, o momento M_Q e o eixo central. Localizar sobre este eixo a resultante R e o momento mínimo M_E do sistema de forças.

## Particularidades da tarefa

1. Os resultados numéricos deverão ser exibidos, preferencialmente, em uma tabela, de modo a facilitar a análise.

2. O(A) aluno(a) deverá provar que o seu programa é capaz de lidar com todos os tipos possíveis de sistemas de forças, abrangendo:

   a) sistemas nulos

   b) sistemas redutíveis a um binário

   c) sistemas redutíveis a uma única força

   d) sistemas redutíveis a força + binário

   Para tanto, deverá apresentar exemplos diversos versando sobre essas 4 categorias de sistemas de força, lembrando que, no caso c, além dos sistemas mais gerais, deverão ser apresentados exemplos de sistemas de forças concorrentes, forças coplanares e forças paralelas.

3. Seria muito conveniente que os pontos P_i de aplicação de forças F_i fossem inseridos em uma figura 3D sólida como, por exemplo, um paralelepípedo, de modo a tornar o problema mais representativo da realidade.

4. Seria conveniente verificar se, no caso particular n = 1, o programa não apresenta singularidades.

5. As figuras em perspectiva devem ser desenhadas escolhendo-se ângulos de visada apropriados à fácil compreensão do observador.

6. O código do programa deve ser anexado aos resultados de suas execuções.

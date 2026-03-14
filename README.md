Chaque dataset contient 1000 vols "record_XX"


Un vol contient 4 éléments : "axis0", "axis1", "block0_items", "block0_values"

axis0 : contient le nom des toutes les cases de l'axe 0 (55)

axis1 : pareil pour l'axe 1 (7429)

block0_items: contient la même chose que axis0 j'ai l'impression

block0_values : matrice de taille (size(axis1),size(axis0)) contenant toutes les valeurs

blockX_values regroupe les colonnes de même type dans des blocs (int, float, etc..) ici il n'y a qu'un seul type (block0_values) donc axis0 = block0_values

les différentes données dont ont a accès:
'ALT [ft]'
'EGT_1 [deg C]'
'EGT_2 [deg C]'
'FMV_1 [mm]'
'FMV_2 [mm]'
'HPTACC_1 [%]'
'HPTACC_2 [%]'
'M [Mach]'
'N1_1 [% rpm]'
'N1_2 [% rpm]'
'N2_1 [% rpm]'
'N2_2 [% rpm]'
'NAIV_1 [bool]'
'NAIV_2 [bool]'
'P0_1 [psia]'
'P0_2 [psia]'
'PRV_1 [bool]'
'PRV_2 [bool]'
'PS3_1 [psia]'
'PS3_2 [psia]'
'PT2_1 [mbar]'
'PT2_2 [mbar]'
'P_OIL_1 [psi]'
'P_OIL_2 [psi]'
'Q_1 [lb/h]'
'Q_2 [lb/h]'
'T1_1 [deg C]'
'T1_2 [deg C]'
'T2_1 [deg C]'
'T2_2 [deg C]'
'T3_1 [deg C]'
'T3_2 [deg C]'
'T5_1 [deg C]'
'T5_2 [deg C]'
'TAT [deg C]'
'TBV_1 [%]'
'TBV_2 [%]'
'TCASE_1 [deg C]'
'TCASE_2 [deg C]'
'TLA_1 [deg]'
'TLA_2 [deg]'
'T_OIL_1 [deg C]'
'T_OIL_2 [deg C]'
'VBV_1 [mm]'
'VBV_2 [mm]'
'VIB_AN1_1 [mils]'
'VIB_AN1_2 [mils]'
'VIB_AN2_1 [ips]'
'VIB_AN2_2 [ips]'
'VIB_BN1_1 [mils]'
'VIB_BN1_2 [mils]'
'VIB_BN2_1 [ips]'
'VIB_BN2_2 [ips]'
'VSV_1 [mm]'
'VSV_2 [mm]'



explication i : engine station from 0 before fan to 5 after nozzle

L’air traverse le moteur dans cet ordre : 

Entrée d’air → Fan → Compresseur → Chambre de combustion → Turbine → Tuyère


Le fan accélère l’air et commence légèrement à le comprimer.

Le compresseur augmente fortement la pression et la température de l’air avant la combustion.

La turbine récupère l’énergie des gaz chauds pour faire tourner le compresseur et le fan.


Station 0 : Avant l’entrée du moteur

Station 1 : entrée du fan

Station 2 : Après le fan / entrée du compresseur

Station 3 : Après le compresseur

Station 4 : Après la chambre de combustion

Station 5 : Après la turbine



CHOIX des variables à garder :


le débit de carburant instantané des deux moteurs:

Q_1 [lb/h] Fuel flow

Q_2 [lb/h]



Variables de puissance moteur:

EGT → température turbine (charge moteur)

EGT_1 [deg C] Exhaust Gaz Temperature

EGT_2 [deg C]


N1 / N2 → régime moteur

N1_1 [% rpm] Speed of secondary shaft (fan)

N1_2 [% rpm]

N2_1 [% rpm] Speed of primary shaft (core)

N2_2 [% rpm]


TLA → position de la manette des gaz

TLA_1 [deg] Level Angle

TLA_2 [deg]



Variables environnementales:

ALT [ft] Altitude

M [Mach] Vitesse

TAT [deg C] Température



Pressions du moteur:

PS3 → pression statique après le compresseur

PS3_1 [psia] Static pressure

PS3_2 [psia]


PT2 → pression totale après le fan

PT2_1 [mbar] Pressure

PT2_2 [mbar]



Températures internes du moteur:

T2 → Température après le fan

T2_1 [deg C]

T2_2 [deg C]


T3 → Température après le compresseur

T3_1 [deg C]

T3_2 [deg C]


T5 → Température après la turbine

T5_1 [deg C]

T5_2 [deg C]



Définition et caractérisation de la phase de montée 

Analyse préliminaire des profils de montée

Afin d’obtenir une première vision des profils de montée, nous avons représenté sur un même graphique les trajectoires d’altitude de cinq vols différents, normalisées de manière à ce que chaque vol débute au point 
(0,0)
(0,0). Cette normalisation permet de comparer plus facilement les formes de montée indépendamment de l’altitude initiale ou du moment exact du décollage.

L’observation de ces profils met en évidence deux comportements principaux de montée.

Le premier correspond à une montée continue, dans laquelle l’altitude augmente de manière relativement régulière jusqu’à atteindre l’altitude de croisière.

Le second type de profil présente l’apparition d’un palier intermédiaire, durant lequel l’avion stabilise temporairement son altitude avant de reprendre sa montée vers l’altitude finale.


Dans la suite de l’étude, il pourra donc être pertinent de séparer les vols en deux catégories :

les vols présentant une montée continue sans palier,

les vols présentant un ou plusieurs paliers intermédiaires.

Cette classification permettra d’analyser plus finement les stratégies de montée et d’adapter les méthodes d’étude aux différents types de profils observés.


Afin de réaliser cette séparation, plusieurs étapes de tri ont été mises en place. L’idée générale repose sur l’identification de phases de stabilisation de l’altitude au cours de la montée. Pour cela, l’algorithme analyse l’évolution de l’altitude à l’aide de fenêtres glissantes contenant un nombre fixe de points consécutifs. Lorsque la variation d’altitude à l’intérieur d’une fenêtre reste inférieure à un certain seuil, cette phase est considérée comme une candidate à un palier.

Toutefois, une altitude stable peut également correspondre au début de la phase de croisière. Afin de distinguer ces deux situations, l’algorithme examine également plusieurs points situés plus loin dans le temps. Si l’altitude augmente de manière significative après la fenêtre stable, la phase est interprétée comme un palier intermédiaire suivi d’une reprise de montée. En revanche, si aucune reprise de montée n’est observée, la stabilisation est considérée comme correspondant à la fin de la montée et au début de la phase de croisière.

Avant de mettre en place cette méthode, il a été nécessaire d’estimer l’intervalle temporel séparant deux mesures successives. Pour cela, un vol présentant une montée continue sans palier a été isolé et analysé. L’étude de la variation d’altitude entre deux points consécutifs a montré une variation moyenne d’environ :

ΔALT≈37 ft

Cette valeur est cohérente avec les taux de montée typiques d’un avion de ligne (de l’ordre de 1500 à 2500 ft/min) et suggère que les données sont échantillonnées à une fréquence d’environ 1 Hz, soit un point par seconde. Cette information permet d’interpréter directement les indices utilisés dans l’algorithme comme des durées en secondes.

Sur cette base, plusieurs paramètres ont été définis afin de détecter les paliers :

taille de la fenêtre glissante : 10 points

soit environ 10 secondes. Une phase est considérée comme potentiellement stable si l’altitude varie très peu sur cette durée. Ce choix permet de filtrer les fluctuations très courtes dues au bruit de mesure tout en restant suffisamment court pour détecter rapidement un changement de régime. Par ailleurs, les paliers intermédiaires observés lors des montées d’avions durent généralement de plusieurs dizaines de secondes à plusieurs minutes, ce qui rend une fenêtre de 10 secondes adaptée pour détecter le début d’une phase de stabilisation sans risquer de manquer ces paliers.

seuil de stabilité : 80 ft

la variation maximale d’altitude dans la fenêtre doit rester inférieure à cette valeur pour être considérée comme un plateau potentiel. Étant donné qu’une montée classique d’un avion de ligne correspond à une augmentation d’environ 30 à 40 ft par seconde, une fenêtre de 10 secondes représenterait normalement une variation de 300 à 400 ft en montée continue. Fixer un seuil de 80 ft permet donc d’identifier des phases où l’altitude évolue très peu par rapport à une montée normale, ce qui correspond à une stabilisation caractéristique d’un palier.

points de vérification futurs : 10, 30 et 200 points

correspondant respectivement à environ 10 s, 30 s et 200 s. L’utilisation de plusieurs horizons temporels permet de vérifier si la montée reprend après une phase stable. Les points proches (10 s) permettent de détecter une reprise rapide de montée, tandis que les points plus éloignés (30 s et 200 s) permettent de confirmer qu’il ne s’agit pas simplement d’une fluctuation momentanée. Le point à 200 secondes permet également de vérifier que la stabilisation observée ne correspond pas directement à la phase de croisière.

seuil de reprise de montée : 200 ft

si l’altitude future dépasse l’altitude de référence de plus de 200 ft, la montée est considérée comme ayant repris. Cette valeur a été choisie afin de dépasser largement les variations d’altitude observées dans un plateau. Une augmentation de 200 ft correspond à plusieurs secondes de montée effective, ce qui permet de distinguer clairement une reprise de montée d’une simple oscillation de l’altitude autour d’une valeur stable.

Une fois ces paramètres définis, l’algorithme parcourt l’ensemble des vols du dataset. Pour chaque vol, plusieurs vérifications préliminaires sont effectuées afin d’éliminer les cas non exploitables (vols trop courts, absence de décollage ou absence de montée identifiable).

Le début de la montée est défini comme le premier instant t0 tel que :

ALT(t0+5)−ALT(t0)>seuil

ce qui permet de détecter une augmentation significative de l’altitude sur quelques secondes.

L’analyse se concentre ensuite sur l’intervalle compris entre ce début de montée et l’altitude maximale atteinte. Les fenêtres glissantes sont utilisées pour identifier les phases de stabilisation. Lorsqu’une fenêtre stable est détectée, l’algorithme vérifie si la montée reprend plus tard dans le profil. Si une reprise de montée est observée, la phase correspond à un palier intermédiaire. Dans le cas contraire, cette stabilisation est interprétée comme le début de la phase de croisière, ce qui marque la fin de la montée.

Ainsi, la fin de montée est définie comme le premier plateau à partir duquel aucune reprise significative de montée n’est observée. Le vol est alors tronqué entre le début de la montée et ce point, puis classé dans la catégorie correspondante : montée avec palier ou montée continue sans palier.

Résumer des 3 fichiers:
Aircraft 1:
Total vols : 1001
Trop courts : 0
Pas de vrai décollage : 4
idx_max trop petit : 0
Pas de début de montée détecté : 0
Début de montée trop tardif : 0
Pas classés : 3
Classés : 994
Avec palier : 447
Sans palier : 550

Aircraft2:
Total vols : 1002
Trop courts : 0
Pas de vrai décollage : 1
idx_max trop petit : 0
Pas de début de montée détecté : 0
Début de montée trop tardif : 0
Pas classés : 0
Classés : 1001
Avec palier : 628
Sans palier : 373

Aircraft3:
Total vols : 1002
Trop courts : 0
Pas de vrai décollage : 2
idx_max trop petit : 0
Pas de début de montée détecté : 0
Début de montée trop tardif : 0
Pas classés : 2
Classés : 998
Avec palier : 611
Sans palier : 389

                    CAPITOUL 2004-2005
     Données moyennes du Mât de Toulouse-Alsace
     ------------------------------------------

Site : Toulouse-Alsace - abréviation = Ta
----

Fichiers :
--------

  Nommage : TaAAAAMM_MAT_%60.asc pour le fichier de données 
            TaAAAAMM_MAT_%60.txt pour le fichier de description
            AAAA = année
            MM = mois
            %60 pour 60 secondes
       Ex : Ta200407_MAT_%60.asc et Ta200407_MAT_%60.txt

  Contenu des fichiers de données :
  -------------------------------

   période mensuelle

   pas d'échantillonage : minute

   17 colonnes, séparées par des espaces.
   
   colonne 1  : la date au format JJ/MM/AAAA
   colonne 2  : l'heure au format HHMMSS.SSS
   colonne 3  : Pression air (hPa), capteur Vaisala PTB200.
   colonne 4  : Température (degrés Celsius), capteur HMP233 VAISALA.
   colonne 5  : Humidité relative (pourcent), capteur HMP233 VAISALA.
   colonne 6  : Rayonnement Global Descendant (watts/m2), capteur CM3 du CNR1 Kipp et Zonen.
   colonne 7  : Rayonnement Global Montant (watts/m2), capteur CM3 du CNR1 Kipp et Zonen.
   colonne 8  : Rayonnement Infra-Rouge Descendant (watts/m2), capteur CG1 du CNR1 Kipp et Zonen.
   colonne 9  : Rayonnement Infra-Rouge Montant (watts/m2), capteur CG1 du CNR1 Kipp et Zonen.
   colonne 10 : Intensité Précipitations mesurée par l'ORG (mm/h)
   colonne 11 : Intensité Précipitations dérivée du pluviomètre à auget (mm/h)
   colonne 12 : Direction du Vent calculée du GILL Haut (degré)
   colonne 13 : Vitesse du Vent calculée du GILL Haut (m/s)
   colonne 14 : Direction du Vent calculée du GILL Bas (degré)
   colonne 15 : Vitesse du Vent calculée du GILL Bas (m/s)
   colonne 16 : Concentration de CO2 du LICOR 7500 (g/m3)
   colonne 17 : Position du Mat  1 = levé
                                 2 = demi-érigé
                                 3 = baissé
  
  Données manquantes : +9999

  Fréquence : Les données sont moyennées à la minute à partir de données échantillonnées à 10 secondes, hormis le vent (GILL à 50 Hz) et le co2 (LICOR à 20 Hz).

  Contenu des fichiers de description :
  -----------------------------------

   13 lignes/fichier de données fournissant des information sur :

      - la constitution des fichiers
      - les paramètres
      - les unités 

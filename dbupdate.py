import spatialite
import time
import os

# Fonction qui se connecte à la DB
def connectToDB(path):
    connector = spatialite.connect(path)
    cursor = connector.cursor()
    print("Connection successful !")

    return connector, cursor

# Fonction qui efface les données d'une table
def clearBoatTable(cursor, table_name):
    
    # On supprime toutes les ligne
    cursor.execute("DELETE FROM " + table_name)
    # On remet le compteur de la clé primaire à zéro
    cursor.execute("DELETE from sqlite_sequence where name='{}'".format(table_name))
    

# Fonction qui print la position et la régions où se trouve le bateau sur la console (débogage)
def getBoatPosition(cursor):
    temp = cursor.execute("SELECT * FROM boat")
    result = cursor.fetchall()
    print(result[0])

def test_existence_table(db,table_name):
    connector, cursor =  connectToDB(db)
    cursor.execute("select name from sqlite_master where name == '{}'".format(table_name))
    liste_table = cursor.fetchall()
    if len(liste_table) == 0:
        resultat = 0
    else:
        resultat = 1
    return(resultat, cursor, connector)

def init_db (db, table_name):
    #tester l'existence du fichier
    # si le fichier n'existe pas, s'y connecter et créer la table
    # si le fichier existe, vérifier que la table existe
    # si la table n'existe pas, la créer
    
    if os.path.exists(db):
        print('fichier existant')
        existence,cursor,connector = test_existence_table(db,table_name)
        if existence == 0:
            print('pas de table')
            pass
        else:
            print('table existante, suppression')
            #cursor.execute("DROP TABLE {}".format(table_name))
            cursor.execute("DELETE FROM " + table_name)
            cursor.execute("DELETE from sqlite_sequence where name='{}'".format(table_name))
            cursor.execute("DROP TABLE {}".format(table_name))
            connector.commit()
            
            print('table supprimée')
    else:
        print('fichier inexistant, initialisaiotn, cela peut prendre un moment ...')
        connector, cursor =  connectToDB(db)
        cursor.execute("SELECT InitSpatialMetaData();")
        print("fin de l initialisation")
        
    existence,cursor,connector = test_existence_table(db,table_name)
    print("creation de la table")
    cursor.execute("CREATE TABLE {} (id_no INTEGER, Geometry)".format(table_name))
    print("ajout colonne geometrie")
    cursor.execute("SELECT RecoverGeometryColumn( '{}', 'Geometry', 4326, 'POINT');".format(table_name))
    print("fin de creation de la table")
    connector.commit()
    return (connector, cursor)

def insert_position(lat,long,db, table):
    connector, cursor =  connectToDB(db)
    clearBoatTable(cursor,table)
    update_boat_query = "insert into {} (id_no, Geometry) values (1, GeomFromText('POINT({} {})',4326))".format(table,long,lat)
    cursor.execute(update_boat_query)
    connector.commit()

# Fonction qui met à jour la position du bateau à en prenant en argument un couple de coordonnées
def updateBoatPosition(lat,long,db,table):
    connector, cursor =  connectToDB(db)
    update_boat_query = "update {} set Geometry = GeomFromText('POINT({} {})',4326) where id_no = 1".format(table, long, lat)
    print("yes")
    cursor.execute(update_boat_query)
    connector.commit()
#--------------------------main -------------------------

# On se connecte à la DB spatiale
# décommenter les deux lignes suivantes pour tester en standalone
#path = "db_boat.sqlite"
#connector, cursor =  init_db(path, 'boat')
#print('initialisation terminée')



"""
# On simule ici un trajet de bateau
temp = 43.5
while True:


    # On remet à zéro la table du bateau
    clearBoatTable(cursor, 'boat')

    # On met à jour la position du bateau
    coordinates = (1.43 ,temp)
    temp += 0.05
    if temp > 49:
        temp = 43.5
    updateBoatPosition(connector, cursor, "boat", coordinates)
    time.sleep(0.3)

"""


""" réunion = 55.5364, -21.1151
     martinique = -61.0242, 14.6415
     ile de france  = 2.3522, 48.8566
     corse = 9.0129 ,42.0396"""

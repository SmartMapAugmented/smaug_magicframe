import fonctions
import sqlite3


#fichier = "C:\JB\smaug\descartes_VR\last_position.csv"

# points à mettre dans un fichier de config

pts1 = ((-498750.821, 6171607.0173),(-1860.48, 891.46))
pts2 = ((-499255.374, 6172148.0898),(-1562.3, 503.1))
pts3 = ((-500281.460, 6170817.010),(-795.4,1311.3))

def recup_coeffs(pts1, pts2,pts3):
    """
    determination des coeff pour conversion unity en x,y geo
    en entrée les points unity et les points geo pour déterminer les coeff
    points = ((Xgeo,Ygeo),(x unity, yunity))
    """
    coeffs = fonctions.det_coeffs(pts1,pts2,pts3)

    return coeffs

def ecrit_position_fichier(position):
    print("ecriture dans fichier : ",str(position))
    f = open(fichier,"w")
    f.write(str(position[0]) + ";"+ str(position[1]))
    f.close()

def lecture_pos_unity(fichier):
    """fonction pour lire la position x y tiré d'un fichier généré par unity"""
    f = open(fichier)
    ligne = f.read()
    print("toto")
    print(ligne)
    l = ligne.replace(", ",";").replace(",",".").split(" ")
    l = l[1].split(";")
    print(l)
    pos = (float(l[0]),float(l[2]))
    print(pos)
    return pos

def conv_unity_geo(pt):
    """pt = point (x,y) unity"""
    coeffs = recup_coeffs(pts1,pts2,pts3)
    pos = fonctions.calc_pos(pt,coeffs)
    print(str(pos))
    return pos

def create_point_sql(BDD, table, x, y ):
    # gère la connection à la BDD SQLITE + l'extension spatiale
    conn = sqlite3.connect(BDD)
    conn.enable_load_extension(True)
    conn.execute('SELECT load_extension("mod_spatialite")')
    # conn.execute("SELECT InitSpatialMetadata(1)")
    cur = conn.cursor()
    requete = f"""insert into {table} (ogc_fid,ogc_fid0,fid,reponse,ogc_id,geometry) values (1, 1, 1, "q1",1,st_buffer(MakePoint({x} , {y} ,3857),100)"""
    cur.execute('SELECT reponse FROM ' + str(table) +
                ' where ST_WITHIN (MakePoint(' + str(long) + ',' + str(lat) + ',3857),Geometry) ')
    rslt = cur.fetchone()

    if not rslt is None:
        result = list(rslt)
        return (str(result[0]))
    else:
        return ('nodata')
    conn.close

fichier = r"C:\JB\smaug\descartes_VR\positionLog.txt"

pts1 = ((-498750.821, 6171607.0173),(-1860.48, 891.46))
pts2 = ((-499255.374, 6172148.0898),(-1562.3, 503.1))
pts3 = ((-500281.460, 6170817.010),(-795.4,1311.3))

pos = lecture_pos_unity(fichier)
BDD = r"C:\JB\smaug\projets git\smaugdetecteurope\super_brest\brest_obcb2024.sqlite"
table = "europe_college_3857"

x = pos[0]
y = pos[1]
fonctions.create_point_sql(BDD, table, x, y )
#conv_unity_geo((0,0))
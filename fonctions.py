from sympy import *  # necessite npmath installe
import sqlite3
import json

# Variables pour la fonction checking_bord
bord_reached = False
w = 600
h = 450

def charge_quizz (fichier_config):
    """fonction pour charger le nom d'un quizz à partir du fichier de config"""
    with open(fichier_config) as json_data:
        params = json.load(json_data)
    for i in params:
        if ("quizz_courant" in i):
            quizz = i["quizz_courant"]
    return quizz


def interro_bdd(BDD,table,champ,lat,long):
    # gère la connection à la BDD SQLITE + l'extension spatiale  
    conn = sqlite3.connect('Interrogation/' +str(BDD)+'.sqlite')
    conn.enable_load_extension(True)
    conn.execute('SELECT load_extension("mod_spatialite")')
    #conn.execute("SELECT InitSpatialMetadata(1)")
    cur = conn.cursor()
    cur.execute('SELECT ' + str(champ)+' FROM ' + str(table)+
                ' where ST_WITHIN (MakePoint(' + str(long) + ',' + str(lat) + ',3857),Geometry) ')
    rslt = cur.fetchone()
    
    if not rslt is None:
        result = list(rslt)
        return(str(result[0]))
    else:
        return ('nodata')
    conn.close

def question_bdd(NomBase,NomTable,X,Y,reponse):
    """
    NomBase : nom du fichier sqlite
    NomTable : nom de la table qui contient les réponse
    X : longitude du point
    Y : latitude du point
    reponse : nom de la réponse
    
    requête : selectionne 
    """
    # gère la connection à la BDD SQLITE + l'extension spatiale  
    fichierBase = NomBase
    print("interrogation de la table dans question_bdd",NomTable)
    conn = sqlite3.connect(fichierBase)
    conn.enable_load_extension(True)
    conn.execute('SELECT load_extension("mod_spatialite")')
    #conn.execute("SELECT InitSpatialMetadata(1)")
    cur = conn.cursor()
    cur.execute('SELECT ogc_fid FROM ' + str(NomTable)+ \
                ' where ST_WITHIN (MakePoint(' + str(X) + ',' + str(Y) + ',3857),geometry) ' + \
                'and reponse = "' + reponse + '"')

    if len(list(cur)) > 0 :
        return 1
    else:
        return 0



def calc_pos(ptX, coeffs):
    """
    :param ptX: point en coordonnees camera (x,y) dont on veut trouver la lat lon
    :param coeffs: coefficients a,b,c,a',b',c' de changement de repere. Sous la forme lon = ax+by+C, lat = a'x+b'y+c'
    Les coefficient sont calcules par la fonction def_coeffs
    :return: point en coordonnee lat, lon (lat,lon)
    """
    print("fonction calcul position", ptX)

    a = coeffs[0]
    b = coeffs[1]
    c = coeffs[2]
    aprim = coeffs[3]
    bprim = coeffs[4]
    cprim = coeffs[5]

    lon = eval(str(a)) * ptX[0] + eval(str(b)) * ptX[1] + eval(str(c))
    lat = eval(str(aprim)) * ptX[0] + eval(str(bprim)) * ptX[1] + eval(str(cprim))

    print("lat lon : ",lat,lon)

    return (lat, lon)



def det_coeffs(ptA, ptB, ptC):
    """
    fonction pour determiner les coefficients a b c et a',b',c'
    en fonction des 3 pts connus
    coord : lata, lona latitude et longitude de a
    xa ya : x et y camera de a

    format pt : ((lat,lon),(x,y))
    """
    print("fonction calcul des coeffs de changement de repere",ptA)
    a, aprim, b, bprim, c, cprim = symbols('a aprim b bprim c cprim')

    print("point dans det_coeff: ", str(ptA), str(ptB), str(ptC))

    eq1 = "a * " + str(ptA[1][0]) + "+ b * " + str(ptA[1][1]) + " + c - " + str(ptA[0][1])
    eq2 = "aprim *" + str(ptA[1][0]) + "+ bprim * " + str(ptA[1][1]) + " + cprim - " + str(ptA[0][0])
    eq3 = "a * " + str(ptB[1][0]) + "+ b * " + str(ptB[1][1]) + " + c - " + str(ptB[0][1])
    eq4 = "aprim *" + str(ptB[1][0]) + "+ bprim * " + str(ptB[1][1]) + " + cprim - " + str(ptB[0][0])
    eq5 = "a * " + str(ptC[1][0]) + "+ b * " + str(ptC[1][1]) + " + c - " + str(ptC[0][1])
    eq6 = "aprim *" + str(ptC[1][0]) + "+ bprim * " + str(ptC[1][1]) + " + cprim - " + str(ptC[0][0])

    coeffs = linsolve([eq1, eq3,
                       eq5],
                      (a, b, c))

    coeffs_prim = linsolve([eq2,
                            eq4,
                            eq6],
                           (aprim, bprim, cprim))

    print(str(coeffs))
    print(str(coeffs_prim))

    (a, b, c) = next(iter(coeffs))
    (aprim, bprim, cprim) = next(iter(coeffs_prim))

    print("coeff:", a, b, c)
    print("coeff prim :", aprim, bprim, cprim)
    
    """ pour config à effacer par la suite
    config["a"] = a
    config["aprim"] = aprim
    config["b"] = b
    config["bprim"] = bprim
    config["c"] = c
    config["cprim"] = cprim
    """
    return (a, b, c, aprim, bprim, cprim)

def test():
    charge_quizz("config.json")

#commenter la ligne suivante pour enlever les tests
test()
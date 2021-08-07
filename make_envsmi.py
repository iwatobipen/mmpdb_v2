from rdkit import Chem
from mmpdblib import environment
import sqlite3

def get_envsmi(constant_smi, radius):
    centers = environment.find_centers(constant_smi)
    res = []
    for atom_id in centers.atom_ids:
        env = Chem.FindAtomEnvironmentOfRadiusN(centers.mol, radius, atom_id)
        submol = Chem.PathToSubmol(centers.mol, env)
        smi = Chem.MolToSmiles(submol)
        res.append(smi)
    return ".".join(res)



def make_environment_smi(mmpdb_con, medchem_move_con, radi=3):
    mmpdb_cur = mmpdb_con.cursor()
    medchem_move_cur = medchem_move_con.cursor()
    sql = f"""SELECT DISTINCT constant_smiles.Smiles
             FROM rule_environment,
                           pair,
                           constant_smiles
             WHERE rule_environment.id = pair.rule_environment_id
             AND pair.constant_id = constant_smiles.id
             AND rule_environment.radius = {radi}
             ;"""
    res = mmpdb_cur.execute(sql)
    for idx, row in enumerate(res.fetchall()):
        env_smi = get_envsmi(row[0], radi)
        try:
            medchem_move_cur.execute("INSERT INTO environment_smi values({env_smi});")
        except:
            print(f"{env_smi} is already exist")
        if idx %% 10000 == 0:
            print(f"{idx} mol proceeded")
    medchem_move_con.commit()
    print("done environment_smi")

def make_environment_fp(mmpdb_con, medchem_move_con, radi=3):
    mmpdb_cur = mmpdb_con.cursor()
    medchem_move_cur = medchem_move_con.cursor()
    sql = f"""SELECT DISTINCT environment_fingerprint.id, environment_fingerprint.fingerprint
              FROM rule_environment, environment_fingerprint 
              WHERE rule_environment.environment_fingerprint_id = environment_fingerprint.id 
              AND rule_environment.radius = {radi}
              ;"""
    fp_info = mmpdb_cur.execute(sql).fetchall()
    for row in fp_info:
        medchem_move_con.execute(f"INSERT INTO environment_fp values({row[0]}, {row[1]});")
    medchem_move_con.commit()
    print("done environment_fp")

def make_fragment_smi(mmpdb_con, medchem_move_con):
    mmpdb_cur = mmpdb_con.cursor()
    medchem_move_cur = medchem_move_con.cursor()
    sql = "SELECT id, smiles FROM rule_smiles;"
    for row in mmpdb_cur.execute(sql).fetchall():
        medchem_move_cur.execute(f"INSERT INTO fragment_smi VALUES(row[0], row[1]);")
    medchem_move_con.commit()
    print("done fragment_smi")


def make_transformations(mmpdb_con, medchem_move_con):
    mmpdb_cur = mmpdb_con.cursor()
    medchem_move_cur = medchem_move_con.cursor()
    sql = """SELECT  

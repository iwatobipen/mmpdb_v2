import make_envsmi
import sqlite3
import argparse
import os

def makeParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('mmpdb', type=str, help='MMPDB')
    parser.add_argument('--transformdb', type=str, help='transformdb', default='transform.db')
    return parser

def make_tranform_db(transformdb:str):
    if os.path.isfile(transformdb):
        os.remove(transformdb)
    con = sqlite3.connect(transformdb)
    cur = con.cursor()
    sql = """CREATE TABLE transformations (lhs_frag INTEGER,
                                            rhs_frag INTEGER, 
                                            envfp INTEGER,
                                            envsmi INTEGER,
                                            radius INTEGER,
                                            frequency INTEGER,
                                            lhs_cpd VARCHAR(255), 
                                            rhs_cpd VARCHAR(255), 
                                            lhs_cpd_id VARCHAR(255),
                                            rhs_cpd_id VARCHAR(255));"""
    cur.execute(sql)
    sql = """CREATE TABLE fragment_smi (id INTEGER, fragsmi VARCHAR(255));"""
    cur.execute(sql)
    sql = """CREATE TABLE environment_smi (id INTEGER PRIMARY KEY AUTOINCREMENT, envsmi VARCHAR(255) UNIQUE);"""
    cur.execute(sql)
    sql = """CREATE TABLE environment_fp (id INTEGER, envfp VARCHAR(43));"""
    cur.execute(sql)
    con.commit()
    con.close()

def insert_env_data(mmpdb:str, transformdb:str):
    from_con = sqlite3.connect(mmpdb)
    from_cur = from_con.cursor()

    to_con = sqlite3.connect(transformdb)
    to_cur = to_con.cursor()
    
    # INSERT DATA TO environment_fp
    print("MAKE environment_fingerprint")
    res = from_cur.execute('SELECT * FROM environment_fingerprint;')
    for idx, row in enumerate(res.fetchall()):
        to_cur.execute(f"INSERT INTO environment_fp (id, envfp) VALUES ({row[0]}, '{row[1]}');")
    to_con.commit()
    print('DONE')

    # INSERT DATA TO fragment_smi
    print('MAKE fragment_smi')
    res = from_cur.execute('SELECT id, smiles FROM rule_smiles;')
    for idx, row in enumerate(res.fetchall()):
        to_cur.execute(f"INSERT INTO fragment_smi (id, fragsmi) VALUES ({row[0]}, '{row[1]}');")
    to_con.commit()
    print('DONE')

    # INSERT DATA TO environment_smi
    print("MAKE environment_smi")
    sql = """SELECT constant_smiles.smiles, rule_env.radius 
            FROM rule_environment rule_env
            JOIN pair ON rule_env.id=pair.rule_environment_id
            JOIN constant_smiles ON pair.constant_id=constant_smiles.id;"""
    res = from_cur.execute(sql)
    for idx, row in enumerate(res.fetchall()):
        if idx+1 % 1000==0:
            print(f'{idx+1} rows processed')
        envsmi = make_envsmi.get_envsmi(row[0], row[1])
        if envsmi == '':
            envsmi = 'NA'
        elif envsmi == '.':
            envsmi = 'NA.NA'
        elif envsmi == '..':
            envsmi = 'NA.NA.NA'
        else:
            envsmi = envsmi
        to_cur.execute(f"INSERT INTO environment_smi (envsmi) SELECT '{envsmi}' WHERE NOT EXISTS (SELECT * FROM environment_smi WHERE envsmi='{envsmi}');")
        to_con.commit()
    to_con.commit()
    print('DONE')
    from_con.close()
    to_con.close()

def insert_transformations_data(mmpdb:str, transformdb:str, debug=False):
    from_con = sqlite3.connect(mmpdb)
    from_cur = from_con.cursor()

    to_con = sqlite3.connect(transformdb)
    to_cur = to_con.cursor()

    if debug:
        to_cur.execute('DROP TABLE transformations;')
        sql = """CREATE TABLE transformations (lhs_frag INTEGER,
                                            rhs_frag INTEGER, 
                                            envfp INTEGER,
                                            envsmi INTEGER,
                                            radius INTEGER,
                                            frequency INTEGER,
                                            lhs_cpd VARCHAR(255), 
                                            rhs_cpd VARCHAR(255), 
                                            lhs_cpd_id VARCHAR(255),
                                            rhs_cpd_id VARCHAR(255));"""
        to_cur.execute(sql)
        to_con.commit()
    
    sql1='''SELECT id, rule_id, COUNT(id), environment_fingerprint_id, radius 
            FROM rule_environment rule_env 
            WHERE rule_env.radius=3  
            GROUP BY rule_env.rule_id;'''
    res = from_cur.execute(sql1)
    for idx, row in enumerate(res.fetchall()):
        #row[0]=id, row[1]=rule_id, row[2]=frequency, 
        #row[3]=environment_fingerprint_id, row[4]=radius
        sql2 = f"""SELECT rule.from_smiles_id,
                        rule.to_smiles_id,
                        rule_env.radius, 
                        constant_smiles.smiles,
                        rule_env.environment_fingerprint_id, 
                        from_cpd.clean_smiles, 
                        to_cpd.clean_smiles,
                        from_cpd.public_id, 
                        to_cpd.public_id 
                    FROM rule_environment rule_env, 
                        rule, 
                        pair, 
                        constant_smiles, 
                        compound from_cpd, 
                        compound to_cpd 
                    WHERE rule_env.rule_id={row[1]} 
                    AND rule_env.rule_id=rule.id 
                    AND rule_env.id=pair.rule_environment_id 
                    AND pair.constant_id=constant_smiles.id 
                    AND pair.compound1_id=from_cpd.id 
                    AND pair.compound2_id=to_cpd.id
                    AND rule_env.radius=3;"""
        data = from_cur.execute(sql2).fetchone()
        envsmi = make_envsmi.get_envsmi(data[3], data[2])
        if envsmi == '':
            envsmi = 'NA'
        elif envsmi == '.':
            envsmi = 'NA.NA'
        elif envsmi == '..':
            envsmi = 'NA.NA.NA'
        else:
            envsmi = envsmi
        sql3 = f"SELECT id FROM environment_smi WHERE envsmi='{envsmi}';"
        envsmi_id = to_cur.execute(sql3).fetchone()[0]
        sql4 = f"""INSERT INTO transformations (lhs_frag, 
                                                rhs_frag, 
                                                envfp, 
                                                envsmi, 
                                                radius, 
                                                frequency, 
                                                lhs_cpd, 
                                                rhs_cpd, 
                                                lhs_cpd_id, 
                                                rhs_cpd_id) VALUES ({data[0]}, 
                                                                    {data[1]}, 
                                                                    {data[4]}, 
                                                                    {envsmi_id}, 
                                                                    {data[2]}, 
                                                                    {row[2]}, 
                                                                    '{data[5]}', 
                                                                    '{data[6]}', 
                                                                    '{data[7]}', 
                                                                    '{data[8]}');"""
        to_cur.execute(sql4)
        to_con.commit()
        if row[2] > 500:
            print(f"frequency {row[2]}")
        if idx % 1000 == 0:
            print(f"{idx} data processed")

        #print(f"radius::{data[2]}, {row[4]}")
    from_con.close()
    to_con.close()
    print('DONE')

if __name__=='__main__':
    parser = makeParser()
    args = parser.parse_args()
    make_tranform_db(args.transformdb)
    insert_env_data(args.mmpdb, args.transformdb)
    insert_transformations_data(args.mmpdb, args.transformdb, debug=False)

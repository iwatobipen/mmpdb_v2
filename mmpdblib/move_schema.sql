CREATE TABLE transformations (
    lhs_frag INTEGER NOT NULL,
    rhs_frag INTEGER NOT NULL,
    envfp INTEGER NOT NULL,
    envsmi INTEGER NOT NULL,
    radius INTEGER NOT NULL,
    frequency INTEGER NOT NULL,
    lhs_cpd VARCHAR(255) NOT NULL ,
    rhs_cpd VARCHAR(255) NOT NULL ,
    lhs_cpd_id INTEGER NOT NULL,
    rhs_cpd_id INTEGER NOT NULL
);

CREATE TABLE fragment_smi (
    id,
    fragmsmi VARCHAR(255) NOT NULL 
);

CREATE TABLE enviromnent_smi(
    id PRIMARY KEY AUTOINCREMENT,
    envsmi VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE enviromnent_fp(
    id,
    envsmi VARCHAR(43) NOT NULL 
);


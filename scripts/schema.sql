CREATE TABLE NonAssemblyAddress (
    address_id                  INTEGER PRIMARY KEY,
    address                     TEXT NOT NULL,
    nr_transactions             INTEGER,
    unique_callers              INTEGER,
    nr_token_transfers          INTEGER,
    is_erc20                    BOOLEAN,
    is_erc721                   BOOLEAN,
    tvl                         INTEGER,
    solidity_version_etherscan  TEXT,
    evm_version                 TEXT,
    block_number                INTEGER,
    loc                         INTEGER,
    hash                        TEXT
);

CREATE TABLE Address (
    address_id                  INTEGER PRIMARY KEY,
    address                     TEXT NOT NULL,
    nr_transactions             INTEGER,
    unique_callers              INTEGER,
    nr_token_transfers          INTEGER,
    is_erc20                    BOOLEAN,
    is_erc721                   BOOLEAN,
    tvl                         INTEGER,
    solidity_version_etherscan  TEXT,
    evm_version                 TEXT,
    block_number                INTEGER,
    loc                         INTEGER,
    hash                        TEXT
);

CREATE TABLE Label (
    label_id    INTEGER PRIMARY KEY,
    label_name  TEXT NOT NULL
);

CREATE TABLE AddressLabel (
    al_id           INTEGER PRIMARY KEY,
    label_id        INTEGER NOT NULL,
    address         TEXT NOT NULL,
    address_type    TEXT,
    tag             TEXT,
    FOREIGN KEY (label_id) REFERENCES Label (label_id)
);

CREATE TABLE SolidityFile (
    file_id             INTEGER PRIMARY KEY,
    file_name           TEXT NOT NULL,
    lines               INTEGER NOT NULL,
    solidity_version    TEXT,
    address_id          INTEGER NOT NULL,
    FOREIGN KEY (address_id)
        REFERENCES Address (address_id)
);

CREATE TABLE Contract (
    contract_id         INTEGER PRIMARY KEY,
    contract_name       TEXT NOT NULL,
    lines               INTEGER NOT NULL,
    funcs               INTEGER NOT NULL,
    funcs_with_assembly INTEGER NOT NULL,
    assembly_fragments  INTEGER NOT NULL,
    assembly_lines      INTEGER NOT NULL,
    has_assembly        BOOLEAN NOT NULL,
    file_id             INTEGER NOT NULL,
    FOREIGN KEY (file_id)
        REFERENCES SolidityFile (file_id)
);

CREATE TABLE Fragment (
    fragment_id     INTEGER PRIMARY KEY,
    lines           INTEGER NOT NULL,
    start_line      INTEGER NOT NULL,
    end_line        INTEGER NOT NULL,
    code            TEXT NOT NULL,
    hash            TEXT NOT NULL,
    contract_id     INTEGER NOT NULL,
    FOREIGN KEY (contract_id)
        REFERENCES Contract (contract_id)
);

CREATE TABLE Opcode (
    opcode_id       INTEGER PRIMARY KEY,
    opcode_name     TEXT NOT NULL
);

CREATE TABLE OpcodesPerFragment (
    opf_id          INTEGER PRIMARY KEY,
    fragment_id     INTEGER NOT NULL,
    opcode_id       INTEGER NOT NULL,
    occurences      INTEGER NOT NULL,
    FOREIGN KEY (fragment_id) REFERENCES Fragment (fragment_id),
    FOREIGN KEY (opcode_id) REFERENCES Opcode (opcode_id)
);

CREATE TABLE OldOpcode (
    old_opcode_id    INTEGER PRIMARY KEY,
    old_opcode_name  TEXT NOT NULL
);

CREATE TABLE OldOpcodesPerFragment (
    oopf_id         INTEGER PRIMARY KEY,
    fragment_id     INTEGER NOT NULL,
    old_opcode_id   INTEGER NOT NULL,
    occurences      INTEGER NOT NULL,
    FOREIGN KEY (fragment_id) REFERENCES Fragment (fragment_id),
    FOREIGN KEY (old_opcode_id) REFERENCES OldOpcode (old_opcode_id)
);

CREATE TABLE HighLevelConstruct (
    high_level_construct_id    INTEGER PRIMARY KEY,
    high_level_construct_name  TEXT NOT NULL
);

CREATE TABLE HighLevelConstructsPerFragment (
    hlc_id                      INTEGER PRIMARY KEY,
    fragment_id                 INTEGER NOT NULL,
    high_level_construct_id     INTEGER NOT NULL,
    occurences                  INTEGER NOT NULL,
    FOREIGN KEY (fragment_id) REFERENCES Fragment (fragment_id),
    FOREIGN KEY (high_level_construct_id)
        REFERENCES HighLevelConstruct (high_level_construct_id)
);

CREATE TABLE Declaration (
    declaration_id    INTEGER PRIMARY KEY,
    declaration_name  TEXT NOT NULL
);

CREATE TABLE DeclarationsPerFragment (
    dpf_id              INTEGER PRIMARY KEY,
    fragment_id         INTEGER NOT NULL,
    declaration_id      INTEGER NOT NULL,
    occurences          INTEGER NOT NULL,
    FOREIGN KEY (fragment_id) REFERENCES Fragment (fragment_id),
    FOREIGN KEY (declaration_id) REFERENCES Declaration (declaration_id)
);

CREATE TABLE SpecialOpcode (
    special_opcode_id    INTEGER PRIMARY KEY,
    special_opcode_name  TEXT NOT NULL
);

CREATE TABLE SpecialOpcodesPerFragment (
    spf_id              INTEGER PRIMARY KEY,
    fragment_id         INTEGER NOT NULL,
    special_opcode_id   INTEGER NOT NULL,
    occurences          INTEGER NOT NULL,
    FOREIGN KEY (fragment_id) REFERENCES Fragment (fragment_id),
    FOREIGN KEY (special_opcode_id) REFERENCES SpecialOpcode (special_opcode_id)
);

CREATE DATABASE IF NOT EXISTS sistema_colas;
USE sistema_colas;

CREATE TABLE IF NOT EXISTS corridas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tiempo DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS colas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    corrida_id INT NOT NULL,
    nombre_id VARCHAR(1) NOT NULL,
    n_entrada INT,
    n_atendidos INT,
    n_no_atendidos INT,
    FOREIGN KEY (corrida_id) REFERENCES corridas(id)
);
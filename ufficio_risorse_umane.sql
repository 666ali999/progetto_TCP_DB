-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Creato il: Nov 19, 2023 alle 19:48
-- Versione del server: 10.4.28-MariaDB
-- Versione PHP: 8.0.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ufficio_risorse_umane`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `dipendenti_ali_ishtiaq`
--

CREATE TABLE `dipendenti_ali_ishtiaq` (
  `id` int(11) NOT NULL,
  `nome` varchar(50) NOT NULL,
  `cognome` varchar(50) NOT NULL,
  `posizione_lavorativa` varchar(50) NOT NULL,
  `data_assunzione` date NOT NULL,
  `residenza` varchar(50) NOT NULL,
  `telefono` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dump dei dati per la tabella `dipendenti_ali_ishtiaq`
--

INSERT INTO `dipendenti_ali_ishtiaq` (`id`, `nome`, `cognome`, `posizione_lavorativa`, `data_assunzione`, `residenza`, `telefono`) VALUES
(1, 'ali', 'ishtiaq', 'studente', '2020-07-15', 'fabbrico', '123445566'),
(2, 'mario', 'rossi', 'insegnante', '2018-06-18', 'milano', '2746553612'),
(3, 'iacopo', 'ferrari', 'calciatore', '2020-09-30', 'modena', '127890302');

-- --------------------------------------------------------

--
-- Struttura della tabella `zone_di_lavoro`
--

CREATE TABLE `zone_di_lavoro` (
  `id_zona` int(11) NOT NULL,
  `nome_zona` varchar(50) NOT NULL,
  `numero_clienti` int(11) NOT NULL,
  `id_dipendente` int(11) DEFAULT NULL,
  `citta` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dump dei dati per la tabella `zone_di_lavoro`
--

INSERT INTO `zone_di_lavoro` (`id_zona`, `nome_zona`, `numero_clienti`, `id_dipendente`, `citta`) VALUES
(1, 'scuola', 1200, 1, 'correggio');

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `dipendenti_ali_ishtiaq`
--
ALTER TABLE `dipendenti_ali_ishtiaq`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `zone_di_lavoro`
--
ALTER TABLE `zone_di_lavoro`
  ADD PRIMARY KEY (`id_zona`),
  ADD KEY `id_dipendente` (`id_dipendente`);

--
-- AUTO_INCREMENT per le tabelle scaricate
--

--
-- AUTO_INCREMENT per la tabella `dipendenti_ali_ishtiaq`
--
ALTER TABLE `dipendenti_ali_ishtiaq`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT per la tabella `zone_di_lavoro`
--
ALTER TABLE `zone_di_lavoro`
  MODIFY `id_zona` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Limiti per le tabelle scaricate
--

--
-- Limiti per la tabella `zone_di_lavoro`
--
ALTER TABLE `zone_di_lavoro`
  ADD CONSTRAINT `zone_di_lavoro_ibfk_1` FOREIGN KEY (`id_dipendente`) REFERENCES `dipendenti_ali_ishtiaq` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

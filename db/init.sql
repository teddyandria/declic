-- Exécuté une seule fois, à la création du volume Postgres.
-- Base séparée pour les tests : ils vident leurs tables, jamais celles de dev.
CREATE DATABASE declic_test OWNER declic;

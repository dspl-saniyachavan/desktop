-- PostgreSQL: Clear parameters table
DELETE FROM parameters;
ALTER SEQUENCE parameters_id_seq RESTART WITH 1;
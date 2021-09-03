/***********************
Author: Rohit Raj
Descripition: Performs the init of tables and indexes for the PostgreSQL database. Database is already created from the console
Created: 2021-06-21
************************/
-- Create the database (already created via UI/init-env-variable)
-- CREATE DATABASE rohit_test

-- Drop the tables
DROP TABLE IF EXISTS authentication_token_info;
DROP TABLE IF EXISTS elasticity_token_info;

-- Create the table

CREATE TABLE authentication_token_info(
   token_id INTEGER GENERATED ALWAYS AS IDENTITY,
   service_name VARCHAR(255) NOT NULL,
   capabilities VARCHAR(255) NOT NULL,
   issued TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   token VARCHAR NOT NULL,
   PRIMARY KEY(token_id)
);

-- Create indexes for faster queries
CREATE INDEX authentication_token_info_service_name_idx ON authentication_token_info (service_name);
CREATE INDEX authentication_token_info_issued_idx ON authentication_token_info USING btree (issued);


CREATE TABLE elasticity_token_info(
   token_id INTEGER GENERATED ALWAYS AS IDENTITY,
   service_name VARCHAR(255) NOT NULL,
   target_service_name VARCHAR(255) NOT NULL,
   capabilities VARCHAR(255) NOT NULL,
   issued TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   token VARCHAR NOT NULL,
   PRIMARY KEY(token_id)
);

-- Create indexes for faster queries
CREATE INDEX elasticity_token_info_service_name_idx ON elasticity_token_info (service_name);
CREATE INDEX elasticity_token_info_service_name_idx ON elasticity_token_info (target_service_name);
CREATE INDEX elasticity_token_info_issued_idx ON elasticity_token_info USING btree (issued);
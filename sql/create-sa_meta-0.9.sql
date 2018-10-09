-- Copyright 2008-2016 by Carnegie Mellon University
-- See license information in LICENSE-OPENSOURCE.txt

create schema sa_meta;

create table sa_meta.versions (
    schema_name text
        constraint "versions.schema_name pkey" primary key,
    version text not null,
    load_time abstime not null default current_timestamp
);
grant select on sa_meta.versions to public;
comment on table sa_meta.versions is
    'Details on which CERT NetSA schemas are installed in this database.';

-- Initial data: what version of the meta-schema is there?
insert into sa_meta.versions ( schema_name, version )
    values ( 'sa_meta', '0.9' );

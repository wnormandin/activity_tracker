#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# DB SCHEMA FILE

full_schema = """
CREATE TABLE `activity` (
    `act_id`    INTEGER PRIMARY KEY AUTOINCREMENT,
    `act_name`  TEXT NOT NULL,
    `act_label` TEXT NOT NULL,
    `act_url`   TEXT NOT NULL,
    `act_desc`  TEXT
);

CREATE TABLE `activitymeta` (
    `meta_id`   INTEGER PRIMARY KEY AUTOINCREMENT,
    `act_id`    INTEGER NOT NULL,
    `act_start` DATE,
    `act_stop`  DATE,
    `act_steps` INTEGER
);

CREATE TABLE `notes` (
    `note_id`   INTEGER PRIMARY KEY AUTOINCREMENT,
    `act_id`    INTEGER NOT NULL,
    `note_timestamp`    DATE DEFAULT (datetime('now','localtime')),
    `note_text` TEXT NOT NULL
);

CREATE TABLE `reports` (
    `report_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `report_date`   DATE,
    `report_type`   TEXT,
    `report_path`   TEXT
);

CREATE TABLE `sysmeta` (
    `user_name` TEXT,
    `system_name`   TEXT,
    `db_created`    DATE,
    `db_updated`    DATE,
    `mod_version`   TEXT
);

CREATE TABLE `tags` (
    `tag_id`    INTEGER PRIMARY KEY AUTOINCREMENT,
    `act_id`    INTEGER NOT NULL,
    `note_id`   INTEGER,
    `tag`   TEXT
);

CREATE UNIQUE INDEX `act_index` ON `activity` (`act_id` ASC,`act_label` ASC);
CREATE INDEX `actlbl_index` ON `activity` (`act_label` ASC);
CREATE UNIQUE INDEX `actmeta_index` ON `activitymeta` (`meta_id` ASC);
CREATE UNIQUE INDEX `note_index` ON `notes` (`note_id` ASC);
CREATE UNIQUE INDEX `tag_index` ON `tags` (`tag_id` ASC);

"""

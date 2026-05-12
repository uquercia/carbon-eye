-- Carbon Eye Campus MySQL bootstrap DDL
-- Source of truth:
-- 1. apps/api/scripts/init_db.py#create_database
-- 2. apps/api/app/models/campus.py
-- Generated against current SQLAlchemy models on 2026-05-12.

CREATE DATABASE IF NOT EXISTS `carbon_eye`
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE `carbon_eye`;

CREATE TABLE `behavior_impacts` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `behavior_name` VARCHAR(80) NOT NULL,
  `category` VARCHAR(40) NOT NULL,
  `description` TEXT NOT NULL,
  `electricity_factor` FLOAT NOT NULL,
  `water_factor` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_behavior_impacts_behavior_name` (`behavior_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `behavior_scores` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `major_code` INTEGER NOT NULL,
  `major_name` VARCHAR(40) NOT NULL,
  `light_off_score` FLOAT NOT NULL,
  `charger_unplug_score` FLOAT NOT NULL,
  `daylight_score` FLOAT NOT NULL,
  `plug_unplug_score` FLOAT NOT NULL,
  `faucet_off_score` FLOAT NOT NULL,
  `shower_short_score` FLOAT NOT NULL,
  `laundry_batch_score` FLOAT NOT NULL,
  `repair_report_score` FLOAT NOT NULL,
  `total_score` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_behavior_scores_major_code` (`major_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `buildings` (
  `id` VARCHAR(64) NOT NULL,
  `name` VARCHAR(80) NOT NULL,
  `zone` VARCHAR(40) NOT NULL,
  `major` VARCHAR(40) NOT NULL,
  `map_x` FLOAT NOT NULL,
  `map_y` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_buildings_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `training_images` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(80) NOT NULL,
  `image_url` VARCHAR(255) NOT NULL,
  `description` TEXT NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `uploaded_images` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `original_filename` VARCHAR(255) NOT NULL,
  `stored_filename` VARCHAR(255) NOT NULL,
  `storage_type` VARCHAR(30) NOT NULL,
  `object_key` VARCHAR(500) NOT NULL,
  `public_url` VARCHAR(500) NOT NULL,
  `content_type` VARCHAR(120) NOT NULL,
  `file_size` INTEGER NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `energy_predictions` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `time_step` INTEGER NOT NULL,
  `building_id` VARCHAR(64) NOT NULL,
  `electricity_actual` FLOAT NOT NULL,
  `electricity_predicted` FLOAT NOT NULL,
  `water_actual` FLOAT NOT NULL,
  `water_predicted` FLOAT NOT NULL,
  `electricity_error` FLOAT NOT NULL,
  `water_error` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_energy_predictions_time_step` (`time_step`),
  CONSTRAINT `fk_energy_predictions_building_id`
    FOREIGN KEY (`building_id`) REFERENCES `buildings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `recognition_samples` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `behavior_name` VARCHAR(80) NOT NULL,
  `location_name` VARCHAR(80) NOT NULL,
  `building_id` VARCHAR(64) NOT NULL,
  `confidence` FLOAT NOT NULL,
  `impact_level` VARCHAR(20) NOT NULL,
  `impact_summary` TEXT NOT NULL,
  `electricity_delta_kwh` FLOAT NOT NULL,
  `water_delta_m3` FLOAT NOT NULL,
  `image_url` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_recognition_samples_building_id`
    FOREIGN KEY (`building_id`) REFERENCES `buildings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `recognition_tasks` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `image_id` INTEGER NOT NULL,
  `status` VARCHAR(40) NOT NULL,
  `model_provider` VARCHAR(60) NOT NULL,
  `model_name` VARCHAR(120) NOT NULL,
  `error_message` TEXT NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `finished_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_recognition_tasks_image_id`
    FOREIGN KEY (`image_id`) REFERENCES `uploaded_images` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `recognition_results` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `task_id` INTEGER NOT NULL,
  `behavior_name` VARCHAR(80) NOT NULL,
  `location_name` VARCHAR(80) NOT NULL,
  `confidence` FLOAT NOT NULL,
  `impact_summary` TEXT NOT NULL,
  `electricity_delta_kwh` FLOAT NOT NULL,
  `water_delta_m3` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_recognition_results_task_id`
    FOREIGN KEY (`task_id`) REFERENCES `recognition_tasks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

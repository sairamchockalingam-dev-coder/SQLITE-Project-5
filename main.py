import sqlite3

import pandas as pd


DATABASE = "experiments.db"


def create_tables(connection):
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS experiments (
            experiment_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            duration_minutes INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS materials (
            material_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS experiment_materials (
            experiment_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            PRIMARY KEY (experiment_id, material_id),
            FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id),
            FOREIGN KEY (material_id) REFERENCES materials(material_id)
        );
        """
    )


def add_sample_data(connection):
    experiments = [
        (1, "Baking Soda Volcano", 5),
        (2, "Crystal Garden", 1440),
        (3, "Rainbow Density Tower", 10),
        (4, "Homemade Slime", 15),
    ]
    materials = [
        (1, "baking soda"),
        (2, "vinegar"),
        (3, "salt"),
        (4, "sugar"),
        (5, "food coloring"),
        (6, "glue"),
        (7, "water"),
    ]
    experiment_materials = [
        (1, 1),
        (1, 2),
        (2, 3),
        (2, 7),
        (3, 4),
        (3, 5),
        (3, 7),
        (4, 5),
        (4, 6),
        (4, 7),
    ]
    connection.executemany(
        "INSERT OR IGNORE INTO experiments VALUES (?, ?, ?)",
        experiments,
    )
    connection.executemany(
        "INSERT OR IGNORE INTO materials VALUES (?, ?)",
        materials,
    )
    connection.executemany(
        "INSERT OR IGNORE INTO experiment_materials VALUES (?, ?)",
        experiment_materials,
    )
    connection.commit()


def show_experiments(connection):
    query = """
        SELECT
            experiments.name AS "Experiment",
            experiments.duration_minutes AS "Duration (minutes)",
            materials.name AS "Material"
        FROM experiments
        JOIN experiment_materials
            ON experiments.experiment_id = experiment_materials.experiment_id
        JOIN materials
            ON experiment_materials.material_id = materials.material_id
        ORDER BY experiments.name, materials.name
    """
    print("\nExperiments and materials")
    print(pd.read_sql_query(query, connection).to_string(index=False))


def find_matching_experiments(connection, material_name):
    query = """
        SELECT
            name AS "Matching experiment",
            duration_minutes AS "Duration (minutes)"
        FROM experiments
        WHERE experiment_id IN (
            SELECT experiment_id
            FROM experiment_materials
            WHERE material_id IN (
                SELECT material_id
                FROM materials
                WHERE name = ?
            )
        )
        ORDER BY name
    """
    matches = pd.read_sql_query(query, connection, params=(material_name,))
    print(f'\nExperiments using "{material_name}"')
    if matches.empty:
        print("No matching experiments found.")
    else:
        print(matches.to_string(index=False))


def find_quickest_experiments(connection):
    query = """
        SELECT
            name AS "Quickest experiment",
            duration_minutes AS "Duration (minutes)"
        FROM experiments
        WHERE duration_minutes = (
            SELECT MIN(duration_minutes)
            FROM experiments
        )
    """
    print("\nQuickest experiment")
    print(pd.read_sql_query(query, connection).to_string(index=False))


def main():
    with sqlite3.connect(DATABASE) as connection:
        create_tables(connection)
        add_sample_data(connection)
        show_experiments(connection)
        material_name = input(
            "\nSearch experiments by material (for example, vinegar): "
        ).strip().lower()
        if material_name:
            find_matching_experiments(connection, material_name)
        find_quickest_experiments(connection)


if __name__ == "__main__":
    main()
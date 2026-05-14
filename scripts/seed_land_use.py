from geoinsight_api.db.session import SessionLocal
from geoinsight_api.seeds.land_use import seed_land_use_data


def main() -> None:
    session = SessionLocal()

    try:
        layer = seed_land_use_data(session)
        print(f"Seeded land-use layer: {layer.id}")
    finally:
        session.close()


if __name__ == "__main__":
    main()

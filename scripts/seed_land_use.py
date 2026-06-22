from geoinsight_api.db.session import SessionLocal
from geoinsight_api.seeds.land_use import seed_land_use_data


def main() -> None:
    session = SessionLocal()

    try:
        layer = seed_land_use_data(session)
        session.commit()
        print(f"Seeded land-use layer: {layer.id}")
    except:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
